 #!/bin/bash

run()
{
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
RESULTS_DIR=./results_spec/$2/$3/$4
NUM_CORES=$5
TRACE_DIR=./tracer/traces

# Instructions
WARMUP=50000000
SIM=50000000

# The temporary file to store the list of commands to run
TMP_COMMAND_FILE=$(mktemp champsim_commands.XXXXXX.tmp)

# Check binary exists
if [ ! -x "$BINARY" ]; then
    echo "❌ Error: Binary $BINARY not found or not executable."
    return 1
fi

# Check traces exist
if [ ! -d "$TRACE_DIR" ] || [ -z "$(ls $TRACE_DIR/*.champsimtrace.xz 2>/dev/null)" ]; then
    echo "❌ Error: No trace files found in $TRACE_DIR"
    return 1
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
        return 1
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
    echo "\"$BINARY\" -warmup_instructions $WARMUP -simulation_instructions $SIM -traces \"$TRACE\" > \"$OUTPUT_FILE\""  >> "$TMP_COMMAND_FILE"

done

NUM_TASKS=$(wc -l < "$TMP_COMMAND_FILE")
echo "✅ Generated $NUM_TASKS simulation commands."
echo "-----------------------------------"


# --- PHASE 2: Execute the commands in parallel using xargs ---
echo "🚀 Running $NUM_TASKS simulations in parallel using $NUM_CORES cores..."

cat "$TMP_COMMAND_FILE" | xargs -I CMD -P "$NUM_CORES" bash -c "CMD"

# --- Cleanup ---
rm "$TMP_COMMAND_FILE"
echo "===================================================================================================================="
echo "✅ All traces completed. Results are in $RESULTS_DIR"
echo "===================================================================================================================="

echo ""
echo "======================================"
echo "$4: Pushing to GitHub"
echo "======================================"


 #Pushing Original directory to GitHub
git add "$RESULTS_DIR"
git commit -m "Update  $3 -- $4 results"
git push origin master


echo ""
echo "======================================"
echo "Pushed to GitHub successfully."
echo "======================================"
echo ""

echo ""
echo "✅ Completed"

}

if [ $# -lt 5 ]|| [ $# -gt 6 ]; then
    echo "Usage: $0 <Prefetcher at L1d> <Perfetcher at L2> <Directory name of Prefetcher's level> <Prefetcher Name Directory> <NUM_CORES> [NO of replacement policy] "
    echo "Example: $0 berti spp pref_l1_l2 berti_spp 20 [Repl. Policy index]"
    echo "Replacement policy Index : { 1:lru 2:srrip 3:drrip 4:hawkeye 5:ship 6:ship++ 7:mockingjay &&  with srrip 8:lru 9:srrip 10:drrip 11:hawkeye 12:ship 13:ship++ 14:mockingjay }"
    exit 1
fi

L1D_PREFETCHER=$1
L2_PREFETCHER=$2

N=${6:-1} # no of Replacement policy

repl_policies=("lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay" "lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay")


for (( j=N; j<=14; j++ )); do
    if (( j < 8 )); then
        #./build.sh "${L1D_PREFETCHER}" "${L2_PREFETCHER}" lru "${repl_policies[$((j-1))]}"
        
        binary="hashed_perceptron-no-${L1D_PREFETCHER}-${L2_PREFETCHER}-no-no-no-no-lru-lru-lru-lru-${repl_policies[$((j-1))]}-lru-lru-lru-1core-no"
        exp_name="exp${j}_lru_${repl_policies[$((j-1))]}"

        if ! run "$binary" "$3" "$4" "$exp_name" "$5"; then
            echo "Run failed for $exp_name — skipping..."
        fi

    else
        #./build.sh "${L1D_PREFETCHER}" "${L2_PREFETCHER}" srrip "${repl_policies[$((j-1))]}"
        
        binary="hashed_perceptron-no-${L1D_PREFETCHER}-${L2_PREFETCHER}-no-no-no-no-lru-lru-lru-srrip-${repl_policies[$((j-1))]}-lru-lru-lru-1core-no"
        exp_name="exp${j}_srrip_${repl_policies[$((j-1))]}"

        if ! run "$binary" "$3" "$4" "$exp_name" "$5"; then
            echo "Run failed for $exp_name — skipping..."
        fi
    fi
done
