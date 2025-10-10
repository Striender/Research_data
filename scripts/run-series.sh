#!/bin/bash

# ============================
# Step 1: Run ChampSim traces
# ============================

if [ $# -lt 4 ] || [ $# -gt 5 ]; then
    echo "Usage: $0 <BINARY_NAME> <CACHE_LEVEL> <PREFETCHER_NAME> <EXP_NO_NAME> [START_TRACE_NAME]"
    exit 1
fi

BINARY=../bin/$1
RESULTS_DIR=../results/$2/$3/$4
TRACE_DIR=../tracer/traces

# Instructions
WARMUP=50000000
SIM=50000000

# Check binary exists
if [ ! -x "$BINARY" ]; then
    echo "❌ Error: Binary $BINARY not found or not executable."
    exit 1
fi

# Check traces exist
if [ ! -d "$TRACE_DIR" ] || [ -z "$(ls $TRACE_DIR/*.champsimtrace.xz 2>/dev/null)" ]; then
    echo "❌ Error: No trace files found in $TRACE_DIR"
    exit 1
fi

# Make results directory if not exists
mkdir -p "$RESULTS_DIR"

# Handle optional start trace
if [ $# -eq 5 ]; then
    START_TRACE_NAME=$5

    # Try to match prefix (e.g., user gives "602.gcc" → matches "602.gcc_s-1850B.champsimtrace.xz")
    MATCHING_TRACE=$(ls "$TRACE_DIR" | grep "^$START_TRACE_NAME" | head -n 1)

    if [ -z "$MATCHING_TRACE" ]; then
        echo "❌ Error: No trace starting with '$START_TRACE_NAME' found in $TRACE_DIR"
        exit 1
    fi

    START_TRACE_NAME="${MATCHING_TRACE%.champsimtrace.xz}"
    echo "🔍 Starting from trace: $START_TRACE_NAME"
fi

# Run simulations
STARTED=false
for TRACE in "$TRACE_DIR"/*.champsimtrace.xz
do
    TRACE_NAME=$(basename "$TRACE" .champsimtrace.xz)

    # If start trace was given, skip until we reach it
    if [ $# -eq 5 ] && [ "$STARTED" = false ]; then
        if [ "$TRACE_NAME" = "$START_TRACE_NAME" ]; then
            STARTED=true
        else
            continue
        fi
    fi

    echo ">>> Running trace: $TRACE_NAME"
    "$BINARY" -warmup_instructions $WARMUP -simulation_instructions $SIM -traces "$TRACE" > "$RESULTS_DIR/$TRACE_NAME"
    echo ">>> Finished trace: $TRACE_NAME"
    echo "-----------------------------------"
done

echo "✅ All traces completed. Results are in $RESULTS_DIR"


# ============================
# Step 2: Extract IPC values
# ============================

# Path to IPC extraction script
EXTRACT_SCRIPT="./extract_IPC.sh"

if [ ! -f "$EXTRACT_SCRIPT" ]; then
    echo "❌ Error: IPC extraction script not found at $EXTRACT_SCRIPT"
    exit 1
fi

echo ""
echo "------------------------------------------------------------------------------------------------------"
echo ""

# Call extract_ipc.sh with arguments:
#   SUBDIR      -> $2
#   ExpNo       -> $3
bash "$EXTRACT_SCRIPT" "$2" "$3" "$4"

echo ""
echo "✅ Completed"
