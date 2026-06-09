#!/bin/bash
set -u
set -o pipefail
# NOTE: intentionally not using set -e

###############################################################################
# INPUTS
###############################################################################
TOTAL_CORES=${1:? "TOTAL_CORES missing"}
RP_SELECTOR=${2:-}

###############################################################################
# PATHS
###############################################################################
TRACE_DIR=/home1/sweta/traces/qualcomm_traces
RESULT_ROOT=./results/results_qualcomm
BIN_DIR=./bin

WARMUP=50000000
SIM=200000000
MAX_CORES_PER_COMBO=64

###############################################################################
# PREFETCHER COMBINATIONS
###############################################################################
PREFETCHER_COMBINATIONS=(
  #"ipcp_isca2020:no"
  #"mlop_dpc3:no"
  #"vberti:no"
  #"ip_stride:no"
#
  #"no:spp"
  #"no:bingo_dpc3"
  #"no:ppf"
  #"no:ip_stride"
  "no:no"
)

###############################################################################
# REPLACEMENT POLICIES
###############################################################################
repl_policies=(
  lru srrip drrip hawkeye ship ship++ mockingjay
  lru srrip drrip hawkeye ship ship++ mockingjay
)

###############################################################################
# BUILD RP LIST
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
# TRACE COUNT & CORE CALCULATION
###############################################################################
TRACE_COUNT=$(ls "$TRACE_DIR"/*.champsimtrace.xz 2>/dev/null | wc -l)
[ "$TRACE_COUNT" -eq 0 ] && { echo "❌ No Qualcomm traces found"; exit 1; }

CORES_PER_COMBO=$TRACE_COUNT
[ "$CORES_PER_COMBO" -gt "$MAX_CORES_PER_COMBO" ] && CORES_PER_COMBO=$MAX_CORES_PER_COMBO

MAX_PARALLEL_COMBOS=$(( TOTAL_CORES / CORES_PER_COMBO ))
[ "$MAX_PARALLEL_COMBOS" -lt 1 ] && MAX_PARALLEL_COMBOS=1

echo "=============================================================="
echo "TOTAL CORES           : $TOTAL_CORES"
echo "QUALCOMM TRACE COUNT  : $TRACE_COUNT"
echo "CORES PER COMBO       : $CORES_PER_COMBO"
echo "PARALLEL COMBINATIONS : $MAX_PARALLEL_COMBOS"
echo "=============================================================="

###############################################################################
# BINARY TOKEN FIX
###############################################################################
binary_name() {
    case "$1" in
        ipcp_isca2020) echo "ipcp_isca2020" ;;
        mlop_dpc3)     echo "mlop_dpc3" ;;
        ip_stride)     echo "ip_stride" ;;
        no)            echo "no" ;;
        *)             echo "$1" ;;
    esac
}
###############################################################################
# RUN QUALCOMM TRACES (INNER PARALLELISM)
###############################################################################
run_qualcomm_traces() {
    local BINARY=$1
    local OUT_DIR=$2

    mkdir -p "$OUT_DIR"
    TMP=$(mktemp)

    for TRACE in "$TRACE_DIR"/*.champsimtrace.xz; do
        TRACE_NAME=$(basename "$TRACE" .champsimtrace.xz)

        # Only server/srv traces
        if [[ ! "$TRACE_NAME" =~ ^(server|srv) ]]; then
            continue
        fi

        if [[ "$TRACE_NAME" == "server_003" ]]; then
            continue
        fi
        echo "\"$BINARY\" \
          -warmup_instructions $WARMUP \
          -simulation_instructions $SIM \
          -traces \"$TRACE\" \
          > \"$OUT_DIR/$TRACE_NAME.out\"" >> "$TMP"
    done

    JOBS=$(wc -l < "$TMP")
    if [ "$JOBS" -eq 0 ]; then
        echo "⚠️  No Qualcomm traces matched filter"
        rm -f "$TMP"
        return
    fi

    echo "🚀 Launching $JOBS traces with $CORES_PER_COMBO cores"
    xargs -P "$CORES_PER_COMBO" -I CMD bash -c CMD < "$TMP"

    rm -f "$TMP"
}

###############################################################################
# RUN ONE COMBINATION
###############################################################################
run_one_combo() {
    local L1=$1
    local L2=$2

    if [[ "$L1" != "no" && "$L2" != "no" ]]; then
        REL="pref_l1_l2/${L1}_${L2}"
    elif [[ "$L1" != "no" ]]; then
        REL="pref_l1/${L1}"
    elif [[ "$L2" != "no" ]]; then
        REL="pref_l2/${L2}"
    else
        REL="baseline"
    fi

    BASE_OUT="$RESULT_ROOT/$REL"

    echo "--------------------------------------------------------------"
    echo "STARTING COMBINATION: $REL"
    echo "--------------------------------------------------------------"

    L1B=$(binary_name "$L1")
    L2B=$(binary_name "$L2")

    for j in "${RP_LIST[@]}"; do
        [ "$j" -le 7 ] && base="lru" || base="srrip"
        pol=${repl_policies[$((j-1))]}

        BIN="$BIN_DIR/hashed_perceptron-no-${L1B}-${L2B}-no-no-no-no-lru-lru-lru-${base}-${pol}-lru-lru-lru-1core-no"

        if [ ! -x "$BIN" ]; then
            echo "❌ Missing binary: $(basename "$BIN")"
            continue
        fi

        EXP_DIR="$BASE_OUT/exp${j}_${base}_${pol}"

        echo "[RUNNING] $REL | RP=$j"
        run_qualcomm_traces "$BIN" "$EXP_DIR"
        echo "[DONE]    $REL | RP=$j"
    done
}

###############################################################################
# OUTER PARALLELISM (SAFE SEMAPHORE)
###############################################################################
running_jobs=0

for combo in "${PREFETCHER_COMBINATIONS[@]}"; do
    IFS=":" read -r L1 L2 <<< "$combo"

    run_one_combo "$L1" "$L2" &

    ((running_jobs++))

    if (( running_jobs >= MAX_PARALLEL_COMBOS )); then
        wait -n
        ((running_jobs--))
    fi
done

wait

echo "=============================================================="
echo "✅ ALL QUALCOMM TRACES COMPLETED SUCCESSFULLY"
echo "=============================================================="
