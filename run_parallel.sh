#!/bin/bash

# ============================
# Step 1: Run ChampSim traces
# ============================

# The 5th argument is now the number of cores to use
if [ $# -lt 5 ] || [ $# -gt 6 ]; then
    echo "Usage: $0 <BINARY_NAME> <CACHE_LEVEL> <PREFETCHER_NAME> <EXP_NO_NAME> <NUM_CORES> [START_TRACE_NAME]"
    echo "Example: $0 my_binary l1_cache spp_dev my_exp 8"
    exit 1
fi

BINARY=./bin/$1
RESULTS_DIR=./results/$2/$3/$4
NUM_CORES=$5
TRACE_DIR=./tracer/traces

# Instructions
WARMUP=50000000
SIM=50000000

# The temporary file to store the list of commands to run
TMP_COMMAND_FILE="champsim_commands.tmp"

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

# --- PHASE 1: Generate the command "to-do list" ---
echo "📝 Preparing command list for parallel execution..."

# Ensure the temporary command file is empty before we start
> "$TMP_COMMAND_FILE"

# Handle optional start trace name
if [ $# -eq 6 ]; then
    START_TRACE_NAME=$6

    # Try to match prefix (e.g., user gives "602.gcc" → matches "602.gcc_s-1850B.champsimtrace.xz")
    MATCHING_TRACE=$(ls "$TRACE_DIR" | grep "^$START_TRACE_NAME" | head -n 1)

    if [ -z "$MATCHING_TRACE" ]; then
        echo "❌ Error: No trace starting with '$START_TRACE_NAME' found in $TRACE_DIR"
        exit 1
    fi

    START_TRACE_NAME="${MATCHING_TRACE%.champsimtrace.xz}"
    echo "🔍 Starting from trace: $START_TRACE_NAME"
fi

# This loop now WRITES commands to a file instead of executing them
STARTED=false
for TRACE in "$TRACE_DIR"/*.champsimtrace.xz
do
    TRACE_NAME=$(basename "$TRACE" .champsimtrace.xz)
    OUTPUT_FILE="$RESULTS_DIR/$TRACE_NAME"

    # If start trace was given, skip until we reach it
    if [ $# -eq 6 ] && [ "$STARTED" = false ]; then
        if [ "$TRACE_NAME" = "$START_TRACE_NAME" ]; then
            STARTED=true
        else
            continue
        fi
    fi

    # Build the full command with proper quoting and append it to our "to-do list"
    echo "\"$BINARY\" -warmup_instructions $WARMUP -simulation_instructions $SIM -traces \"$TRACE\" > \"$OUTPUT_FILE\"" >> "$TMP_COMMAND_FILE"

done

NUM_TASKS=$(wc -l < "$TMP_COMMAND_FILE")
echo "✅ Generated $NUM_TASKS simulation commands."
echo "-----------------------------------"


# --- PHASE 2: Execute the commands in parallel using xargs ---
echo "🚀 Running $NUM_TASKS simulations in parallel using $NUM_CORES cores..."

cat "$TMP_COMMAND_FILE" | xargs -I CMD -P "$NUM_CORES" bash -c "CMD"

# --- Cleanup ---
rm "$TMP_COMMAND_FILE"

echo "✅ All traces completed. Results are in $RESULTS_DIR"


# ============================
# Step 2: Extract IPC values
# ============================

# Path to IPC extraction script
cd scripts
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