#!/bin/bash
set -u
set -o pipefail

###############################################################################
# INPUTSS
###############################################################################
TOTAL_CORES=${1:? "TOTAL_CORES required"}
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
TRACE_DIR=/home1/sweta/traces/DPC4-Traces/AI_ML
RESULT_ROOT=./results/ai_ml/bingo_32KB
BIN_DIR=./bin

SKIP_TRACE_PREFIXES=(
    rwkv
    biogpt.cpp-ggml-model-tocilizumab
)

WARMUP=50000000
SIM=200000000
MAX_CORES_PER_COMBO=26

###############################################################################
# PREFETCHER COMBINATIONS
###############################################################################
PREFETCHER_COMBINATIONS=(
 #d  "ipcp_isca2020:ppf"
 #d "ipcp_isca2020:bingo_dpc3"
 #d "ipcp_isca2020:spp"
 #d "ipcp_isca2020:ip_stride"
#d
 #d "vberti:ppf"
 #d "vberti:spp"
#"vberti:bingo_dpc3"
 # "vberti:ip_stride"
#d
 #d "mlop_dpc3:ip_stride"
 #d "mlop_dpc3:ppf"
 #d "mlop_dpc3:spp"
 #d "mlop_dpc3:bingo_dpc3"
#d
 #d "ip_stride:ppf"
 #d "ip_stride:bingo_dpc3"
 #d "ip_stride:spp"

  #"ipcp_isca2020:no"
  #"mlop_dpc3:no"
  #"vberti:no"
  #"ip_stride:no"
  #"no:spp"
  "no:bingo_dpc3"
  #"no:ppf"
  #"no:ip_stride"
  #"no:sms"
 #"no:no"
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
echo "RP_SELECTOR = $RP_SELECTOR"
echo "RP_LIST     = ${RP_LIST[*]}"
###############################################################################
# TRACE / CORE CALCULATION
###############################################################################
TRACE_COUNT=0
for TRACE in "$TRACE_DIR"/*.champsimtrace.gz; do
    TRACE_FILE=$(basename "$TRACE")

    skip_trace=false
    for prefix in "${SKIP_TRACE_PREFIXES[@]}"; do
        if [[ "$TRACE_FILE" == "$prefix"* ]]; then
            skip_trace=true
            break
        fi
    done

    [[ "$skip_trace" == true ]] && continue
    ((TRACE_COUNT++))
done

CORES_PER_COMBO=$TRACE_COUNT
[ "$CORES_PER_COMBO" -gt "$MAX_CORES_PER_COMBO" ] && CORES_PER_COMBO=$MAX_CORES_PER_COMBO

MAX_PARALLEL_COMBOS=$(( TOTAL_CORES / CORES_PER_COMBO ))
[ "$MAX_PARALLEL_COMBOS" -lt 1 ] && MAX_PARALLEL_COMBOS=1

echo "=============================================================="
echo "TOTAL CORES           : $TOTAL_CORES"
echo "TRACE COUNT           : $TRACE_COUNT"
echo "CORES PER COMBO       : $CORES_PER_COMBO"
echo "PARALLEL COMBINATIONS : $MAX_PARALLEL_COMBOS"
echo "=============================================================="

###############################################################################
# PREFETCHER NAME → BINARY TOKEN
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
# RUN TRACES (SKIPS excluded traces)
###############################################################################
run_traces() {
    local BINARY=$1
    local OUT_DIR=$2

    mkdir -p "$OUT_DIR"
    local TMP
    TMP=$(mktemp)

    for TRACE in "$TRACE_DIR"/*.champsimtrace.gz; do
        TRACE_FILE=$(basename "$TRACE")

        # 🚫 Skip excluded traces
        skip_trace=false
        for prefix in "${SKIP_TRACE_PREFIXES[@]}"; do
            if [[ "$TRACE_FILE" == "$prefix"* ]]; then
                skip_trace=true
                break
            fi
        done

        [[ "$skip_trace" == true ]] && continue

        NAME="${TRACE_FILE%.champsimtrace.gz}"

        echo "\"$BINARY\" \
          -warmup_instructions $WARMUP \
          -simulation_instructions $SIM \
          -traces \"$TRACE\" \
          > \"$OUT_DIR/$NAME\"" >> "$TMP"
    done

    JOBS=$(wc -l < "$TMP")

    TRACE_PARALLEL=$CORES_PER_COMBO

    if [[ "$RP_MODE" == "p" ]]; then

        RP_COUNT=${#RP_LIST[@]}

        # divide available cores across RPs
        TRACE_PARALLEL=$(( TOTAL_CORES / MAX_PARALLEL_COMBOS ))

        [ "$TRACE_PARALLEL" -lt 1 ] && TRACE_PARALLEL=1

        [ "$TRACE_PARALLEL" -gt "$CORES_PER_COMBO" ] && \
            TRACE_PARALLEL=$CORES_PER_COMBO
    fi

    echo "🚀 Launching $JOBS traces using $TRACE_PARALLEL cores"

    xargs -P "$TRACE_PARALLEL" -I CMD bash -c CMD < "$TMP"
    rm -f "$TMP"
}

###############################################################################
# RUN SINGLE RP
###############################################################################
run_single_rp() {
    local L1_BIN=$1
    local L2_BIN=$2
    local PREF_DIR=$3
    local j=$4

    [ "$j" -le 7 ] && base="lru" || base="srrip"
    pol=${repl_policies[$((j-1))]}

    binary="$BIN_DIR/hashed_perceptron-no-${L1_BIN}-${L2_BIN}-no-no-no-no-lru-lru-lru-${base}-${pol}-lru-lru-lru-1core-no"

    if [ ! -x "$binary" ]; then
        echo "❌ Binary not found: $binary"
        return 1
    fi

    exp_dir="$RESULT_ROOT/$PREF_DIR/exp${j}_${base}_${pol}"

    echo "[RUNNING] $PREF_DIR | RP=$j | ${base}/${pol}"
    run_traces "$binary" "$exp_dir"
    echo "[DONE]    $PREF_DIR | RP=$j"
}
 
###############################################################################
# RUN ONE COMBINATION
###############################################################################
run_one_combo() {
    local L1=$1
    local L2=$2
    shift 2
    local RP_LIST_LOCAL=("$@")

    if [[ "$L1" != "no" && "$L2" != "no" ]]; then
        PREF_DIR="pref_l1_l2/${L1}_${L2}"
    elif [[ "$L1" != "no" ]]; then
        PREF_DIR="pref_l1/${L1}"
    elif [[ "$L2" != "no" ]]; then
        PREF_DIR="pref_l2/${L2}"
    else
        PREF_DIR="baseline"
    fi

    L1_BIN=$(binary_name "$L1")
    L2_BIN=$(binary_name "$L2")

    if [[ "$RP_MODE" == "p" ]]; then

        echo "🚀 Running replacement policies in parallel for $PREF_DIR"

        RP_PARALLEL=$MAX_PARALLEL_COMBOS

        rp_jobs=0

        for j in "${RP_LIST_LOCAL[@]}"; do

            run_single_rp "$L1_BIN" "$L2_BIN" "$PREF_DIR" "$j" &

            ((rp_jobs++))

            if (( rp_jobs >= RP_PARALLEL )); then
                wait -n
                ((rp_jobs--))
            fi

        done

        wait

    else

        for j in "${RP_LIST_LOCAL[@]}"; do
            run_single_rp "$L1_BIN" "$L2_BIN" "$PREF_DIR" "$j"
        done

    fi
}

###############################################################################
# OUTER PARALLELISM
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
echo "✅ ALL AI/ML TRACES COMPLETED SUCCESSFULLY"
echo "=============================================================="



