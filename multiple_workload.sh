#!/bin/bash
set -e

############################################
# CONFIG
############################################

declare -A TRACE_SUITES=(
  [qualcomm]="/home1/sweta/traces/qualcomm_traces/"
  [spec]="/home2/neeraj/Berti-MICRO2022/ChampSim/Other_PF/tracer/traces"
  [gap]="/home1/sweta/traces/gaptraces/"
  [ai_ml]="/home1/sweta/traces/DPC4-Traces/AI_ML/"
  [google]="/home1/sweta/traces/DPC4-Traces/Google_Traces_v2/Google_Traces_v2/"
)

repl_policies=(
  "lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay"
  "lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay"
)

WARMUP=50000000
SIM=50000000

############################################
# USAGE
############################################
if [ $# -lt 8 ]; then
  echo "Usage:"
  echo "$0 <trace_suite|all> <trace_list|ALL> <rp_list|ALL> <L1D> <L2> <cache_dir> <pref_dir> <num_cores>"
  exit 1
fi

TRACE_SUITE=$1
TRACE_LIST=$2
RP_LIST=$3
L1D=$4
L2=$5
CACHE_DIR=$6
PREF_DIR=$7
NUM_CORES=$8

TMP_CMD=$(mktemp champsim_cmds.XXXX)
RESULTS_BASE=./results/$CACHE_DIR/$PREF_DIR

############################################
# LOAD TRACE FILTER
############################################
declare -A TRACE_FILTER
if [ "$TRACE_LIST" != "ALL" ]; then
  while read -r t; do TRACE_FILTER["$t"]=1; done < "$TRACE_LIST"
fi

############################################
# LOAD RP FILTER
############################################
declare -A RP_FILTER
if [ "$RP_LIST" != "ALL" ]; then
  while read -r r; do RP_FILTER["$r"]=1; done < "$RP_LIST"
fi

############################################
# BUILD + RUN
############################################
run_suite () {
  local suite=$1
  local dir=${TRACE_SUITES[$suite]}

  for ((j=1; j<=14; j++)); do

    if [ "$RP_LIST" != "ALL" ] && [ -z "${RP_FILTER[$j]}" ]; then
      continue
    fi

    if (( j < 8 )); then
      base=lru
    else
      base=srrip
    fi

    pol=${repl_policies[$((j-1))]}
    EXP_NAME="exp${j}_${base}_${pol}"

    BINARY="./bin/hashed_perceptron-no-${L1D}-${L2}-no-no-no-no-lru-lru-lru-${base}-${pol}-lru-lru-lru-1core-no"
    OUT_DIR="$RESULTS_BASE/$EXP_NAME"
    mkdir -p "$OUT_DIR"

    for trace in "$dir"/*.champsimtrace.xz; do
      TNAME=$(basename "$trace" .champsimtrace.xz)

      if [ "$TRACE_LIST" != "ALL" ] && [ -z "${TRACE_FILTER[$TNAME]}" ]; then
        continue
      fi

      echo "\"$BINARY\" \
        -warmup_instructions $WARMUP \
        -simulation_instructions $SIM \
        -traces \"$trace\" > \"$OUT_DIR/$suite-$TNAME\"" >> "$TMP_CMD"
    done
  done
}

############################################
# EXECUTION
############################################
> "$TMP_CMD"

if [ "$TRACE_SUITE" = "all" ]; then
  for s in "${!TRACE_SUITES[@]}"; do
    run_suite "$s"
  done
else
  run_suite "$TRACE_SUITE"
fi

wc -l "$TMP_CMD"
cat "$TMP_CMD" | xargs -P "$NUM_CORES" -I CMD bash -c "CMD"

rm "$TMP_CMD"
echo "✅ Done"
