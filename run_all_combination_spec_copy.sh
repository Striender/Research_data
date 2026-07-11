#!/bin/bash
set -u
set -o pipefail

###############################################################################
# USAGE
# ./run_spec_master.sh <TOTAL_CORES> [RP_SELECTOR]
###############################################################################

###############################################################################
# INPUTS
###############################################################################
TOTAL_CORES=${1:? "TOTAL_CORES missing"}

RP_SELECTOR=""
RP_MODE="sequential"

if [[ $# -ge 2 ]]; then
    if [[ "$2" == "p" ]]; then
        RP_MODE="p"
    else
        RP_SELECTOR="$2"
    fi
fi

if [[ $# -ge 3 ]]; then
    RP_MODE="$3"
fi

###############################################################################
# PATHS & CONSTANTS
###############################################################################
TRACE_DIR=./tracer/traces
RESULT_ROOT=./results/spec/L1d_KB
BIN_DIR=./bin

WARMUP=50000000
SIM=200000000
MAX_CORES_PER_COMBO=64

###############################################################################
# PREFETCHER COMBINATIONS
###############################################################################
PREFETCHER_COMBINATIONS=( 
  #"ipcp_isca2020:bingo_dpc3"
  #"ipcp_isca2020:spp"
  #"ipcp_isca2020:ip_stride"
  #"vberti:ppf"
  #"vberti:spp"
  "vberti:bingo_dpc3"
  "vberti:ip_stride"
#
  #"mlop_dpc3:ip_stride" 
  #"mlop_dpc3:spp"
  #"mlop_dpc3:bingo_dpc3"
  #
#
  #"ipcp_isca2020:no"
  #"mlop_dpc3:no"
  #"vberti:no" 

  #"no:spp"
  #"no:bingo_dpc3"
  #"no:ppf"
  #"no:ip_stride"
  #"no:no"
)

###############################################################################
# Replacement policies
###############################################################################
repl_policies=(
  lru srrip drrip hawkeye ship ship++ mockingjay
  lru srrip drrip hawkeye ship ship++ mockingjay
)

###############################################################################
# Build RP list
###############################################################################
RP_LIST=()

if [ -z "$RP_SELECTOR" ]; then
    RP_LIST=($(seq 1 14))
elif [[ "$RP_SELECTOR" =~ ^[0-9]+$ ]]; then
    RP_LIST=("$RP_SELECTOR")
elif [[ "$RP_SELECTOR" == rp:* ]]; then
    IFS=',' read -ra RP_LIST <<< "${RP_SELECTOR#rp:}"
else
    echo "❌ Invalid RP selector"
    exit 1
fi

###############################################################################
# Core utilization logic
###############################################################################
TRACE_COUNT=$(ls "$TRACE_DIR"/*.champsimtrace.xz 2>/dev/null | wc -l)
[ "$TRACE_COUNT" -eq 0 ] && { echo "❌ No SPEC traces found"; exit 1; }

CORES_PER_COMBO=$TRACE_COUNT
[ "$CORES_PER_COMBO" -gt "$MAX_CORES_PER_COMBO" ] && CORES_PER_COMBO=$MAX_CORES_PER_COMBO

MAX_PARALLEL_COMBOS=$(( TOTAL_CORES / CORES_PER_COMBO ))
[ "$MAX_PARALLEL_COMBOS" -lt 1 ] && MAX_PARALLEL_COMBOS=1

echo "=============================================================="
echo "SPEC TRACE COUNT       : $TRACE_COUNT"
echo "CORES PER COMBINATION  : $CORES_PER_COMBO"
echo "TOTAL CORES            : $TOTAL_CORES"
echo "PARALLEL COMBINATIONS  : $MAX_PARALLEL_COMBOS"
echo "=============================================================="

###############################################################################
# Directory naming (simple & consistent)
###############################################################################
get_pref_dir() {
    local L1=$1
    local L2=$2

    if [[ "$L1" != "no" && "$L2" != "no" ]]; then
        echo "pref_l1_l2/${L1}_${L2}"
    elif [[ "$L1" != "no" ]]; then
        echo "pref_l1/${L1}"
    elif [[ "$L2" != "no" ]]; then
        echo "pref_l2/${L2}"
    else
        echo "baseline"
    fi
}

###############################################################################
# Run SPEC traces in parallel (INNER LEVEL)
###############################################################################
run_spec_traces() {
    local BINARY=$1
    local OUT_DIR=$2

    mkdir -p "$OUT_DIR"
    local TMP
    TMP=$(mktemp)

    for TRACE in "$TRACE_DIR"/*.champsimtrace.xz; do
        NAME=$(basename "$TRACE" .champsimtrace.xz)
        echo "\"$BINARY\" \
          -warmup_instructions $WARMUP \
          -simulation_instructions $SIM \
          -traces \"$TRACE\" \
          > \"$OUT_DIR/$NAME.out\"" >> "$TMP"
    done

    # Determine how many trace jobs to run in parallel
    TRACE_PARALLEL=$CORES_PER_COMBO

    echo "🚀 Launching $(wc -l < "$TMP") SPEC traces using $TRACE_PARALLEL cores"

    xargs -P "$TRACE_PARALLEL" -I CMD bash -c CMD < "$TMP"

    rm -f "$TMP"
}


###############################################################################
# RUN SINGLE RP
###############################################################################
run_single_rp() {
    local L1=$1
    local L2=$2
    local BASE_OUT=$3
    local j=$4

    [ "$j" -le 7 ] && base="lru" || base="srrip"
    pol=${repl_policies[$((j-1))]}

    binary="$BIN_DIR/hashed_perceptron-no-${L1}-${L2}-no-no-no-no-lru-lru-lru-${base}-${pol}-lru-lru-lru-1core-no"

    if [ ! -x "$binary" ]; then
        echo "❌ Binary missing: $binary"
        return 1
    fi

    EXP_DIR="$BASE_OUT/exp${j}_${base}_${pol}"

    echo "[RUNNING] RP=$j (${base}/${pol})"
    run_spec_traces "$binary" "$EXP_DIR"
    echo "[DONE] RP=$j (${base}/${pol})"
}

###############################################################################
# Run ONE prefetcher combination
###############################################################################
run_one_combo() {
    local L1=$1
    local L2=$2
    shift 2
    local RP_LIST_LOCAL=("$@")

    local REL_PATH
    REL_PATH=$(get_pref_dir "$L1" "$L2")
    local BASE_OUT="$RESULT_ROOT/$REL_PATH"

    echo "--------------------------------------------------------------"
    echo "STARTING SPEC COMBO: $REL_PATH"
    echo "--------------------------------------------------------------"

    if [[ "$RP_MODE" == "p" ]]; then

        echo "🚀 Running replacement policies in parallel"
    
        RP_PARALLEL=$MAX_PARALLEL_COMBOS
    
        rp_jobs=0
    
        for j in "${RP_LIST_LOCAL[@]}"; do
    
            run_single_rp "$L1" "$L2" "$BASE_OUT" "$j" &
    
            ((rp_jobs++))
    
            if (( rp_jobs >= RP_PARALLEL )); then
                wait -n
                ((rp_jobs--))
            fi
    
        done
    
        wait

    else

        for j in "${RP_LIST_LOCAL[@]}"; do
            run_single_rp "$L1" "$L2" "$BASE_OUT" "$j"
        done

    fi

    echo "COMPLETED SPEC COMBO: $REL_PATH"
}

###############################################################################
# OUTER PARALLELISM (ROBUST SEMAPHORE)
###############################################################################
if [[ "$RP_MODE" == "p" ]]; then

    for combo in "${PREFETCHER_COMBINATIONS[@]}"; do
        IFS=":" read -r L1 L2 <<< "$combo"

        run_one_combo "$L1" "$L2" "${RP_LIST[@]}"
    done

else

    running_jobs=0

    for combo in "${PREFETCHER_COMBINATIONS[@]}"; do
        IFS=":" read -r L1 L2 <<< "$combo"

        run_one_combo "$L1" "$L2" "${RP_LIST[@]}" &

        ((running_jobs++))

        if (( running_jobs >= MAX_PARALLEL_COMBOS )); then
            wait -n
            ((running_jobs--))
        fi
    done

    wait

fi

echo "=============================================================="
echo "✅ ALL SPEC EXPERIMENTS COMPLETED"
echo "=============================================================="
