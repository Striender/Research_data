#!/bin/bash
set -u
set -o pipefail

###############################################################################
# INPUTS
###############################################################################
TOTAL_CORES=${1:? "TOTAL_CORES not provided"}
RP_SELECTOR=${2:-}

###############################################################################
# PATHS & CONSTANTS
###############################################################################
TRACE_DIR=/home1/sweta/traces/gaptraces
RESULT_ROOT=./loopCount/results/results_gap
BIN_DIR=./bin

WARMUP=50000000
SIM=200000000
MAX_CORES_PER_COMBO=64

###############################################################################
# Prefetcher combinations
###############################################################################
PREFETCHER_COMBINATIONS=(
 #d  "ipcp_isca2020:ppf"
 #d "ipcp_isca2020:bingo_dpc3"
 #d "ipcp_isca2020:spp"
 #d "ipcp_isca2020:ip_stride"
#d
 #d "vberti:ppf"
 #d "vberti:spp"
 #d "vberti:bingo_dpc3"
 #d "vberti:ip_stride"
#d
 #d "mlop_dpc3:ip_stride"
 #d "mlop_dpc3:ppf"
 #d "mlop_dpc3:spp"
 #d "mlop_dpc3:bingo_dpc3"
#d
 #d "ip_stride:ppf"
 #d "ip_stride:bingo_dpc3"
 #d "ip_stride:spp"

  "ipcp_isca2020:no"
  "mlop_dpc3:no"
  "vberti:no"
  "ip_stride:no"
  "no:spp"
  "no:bingo_dpc3"
  "no:ppf"
  "no:ip_stride"
  "no:no"
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
# Trace / core calculation
###############################################################################
TRACE_COUNT=$(ls "$TRACE_DIR"/*.trace.gz 2>/dev/null | wc -l)
[ "$TRACE_COUNT" -eq 0 ] && { echo "❌ No GAP traces found"; exit 1; }

CORES_PER_COMBO=$TRACE_COUNT
[ "$CORES_PER_COMBO" -gt "$MAX_CORES_PER_COMBO" ] && CORES_PER_COMBO=$MAX_CORES_PER_COMBO

MAX_PARALLEL_COMBOS=$(( TOTAL_CORES / CORES_PER_COMBO ))
[ "$MAX_PARALLEL_COMBOS" -lt 1 ] && MAX_PARALLEL_COMBOS=1

echo "=============================================================="
echo "TOTAL CORES           : $TOTAL_CORES"
echo "TRACES PER COMBO      : $TRACE_COUNT"
echo "CORES PER COMBO       : $CORES_PER_COMBO"
echo "PARALLEL COMBINATIONS : $MAX_PARALLEL_COMBOS"
echo "=============================================================="

###############################################################################
# Directory naming (unchanged logic, safer form)
###############################################################################
get_pref_group_and_dir() {
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
# Run traces in parallel (INNER LEVEL)
###############################################################################
run_traces() {
    local BINARY=$1
    local OUT_DIR=$2

    mkdir -p "$OUT_DIR"
    local TMP
    TMP=$(mktemp)

    for TRACE in "$TRACE_DIR"/*.trace.gz; do
        NAME=$(basename "$TRACE" .trace.gz)
        echo "\"$BINARY\" \
          -warmup_instructions $WARMUP \
          -simulation_instructions $SIM \
          -traces \"$TRACE\" \
          > \"$OUT_DIR/$NAME.out\"" >> "$TMP"
    done

    echo "🚀 Launching $(wc -l < "$TMP") traces using $CORES_PER_COMBO cores"
    xargs -P "$CORES_PER_COMBO" -I CMD bash -c CMD < "$TMP"

    rm -f "$TMP"
}

###############################################################################
# Run one prefetcher combination
###############################################################################
run_one_combo() {
    local L1=$1
    local L2=$2
    shift 2
    local RP_LIST_LOCAL=("$@")

    local REL_PATH
    REL_PATH=$(get_pref_group_and_dir "$L1" "$L2")
    local BASE_OUT="$RESULT_ROOT/$REL_PATH"

    echo "--------------------------------------------------------------"
    echo "STARTING COMBINATION: $REL_PATH"
    echo "--------------------------------------------------------------"

    for j in "${RP_LIST_LOCAL[@]}"; do
        [ "$j" -le 7 ] && base="lru" || base="srrip"
        pol=${repl_policies[$((j-1))]}

        binary="$BIN_DIR/hashed_perceptron-no-${L1}-${L2}-no-no-no-no-lru-lru-lru-${base}-${pol}-lru-lru-lru-1core-no"

        if [ ! -x "$binary" ]; then
            echo "❌ Binary missing: $binary"
            exit 1
        fi

        exp_dir="$BASE_OUT/exp${j}_${base}_${pol}"

        echo "[RUNNING] $REL_PATH | RP=$j"
        run_traces "$binary" "$exp_dir"
        echo "[DONE]    $REL_PATH | RP=$j"
    done
}

###############################################################################
# OUTER PARALLELISM (CORRECT SEMAPHORE)
###############################################################################
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

echo "=============================================================="
echo "✅ ALL GAP TRACES COMPLETED SUCCESSFULLY"
echo "=============================================================="
