#!/bin/bash

###############################################################################
# MASTER SCRIPT: Dispatch to workload-specific scripts
###############################################################################

if [ "$#" -lt 2 ]; then
    echo "ERROR: Missing arguments"
    echo ""
    echo "Usage:"
    echo "./run_all_combination.sh <workload> <args...>"
    echo ""
    echo "Workloads:"
    echo "  google   -> Google DPC-4 traces"
    echo "  ai_ml    -> AI/ML traces (rwkv skipped)"
    echo "  gap      -> GAP traces"
    echo "  spec     -> SPEC traces"
    echo "  qualcomm -> Qualcomm traces"
    echo ""
    echo "Example:"
    echo "./run_all_combination.sh google berti spp pref_l1_l2 berti_spp 32 14"
    exit 1
fi

WORKLOAD=$1
shift   # remove workload from argument list

###############################################################################
# Workload dispatch table
###############################################################################

case "$WORKLOAD" in
    google)
        SCRIPT="./run_all_combination_google.sh"
        ;;
    ai_ml|aiml)
        SCRIPT="./run_all_combination_ai_ml.sh"
        ;;
    gap)
        SCRIPT="./run_all_combination_gap.sh"
        ;;
    spec)
        SCRIPT="./run_all_combination_spec.sh"
        ;;
    qualcomm)
        SCRIPT="./run_all_combination_qualcomm.sh"
        ;;
    *)
        echo "ERROR: Unknown workload '$WORKLOAD'"
        echo "Valid workloads: google, ai_ml, gap, spec, qualcomm"
        exit 1
        ;;
esac

###############################################################################
# Safety checks
###############################################################################

if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: Script $SCRIPT not found"
    exit 1
fi

if [ ! -x "$SCRIPT" ]; then
    echo "ERROR: Script $SCRIPT is not executable"
    echo "Run: chmod +x $SCRIPT"
    exit 1
fi

###############################################################################
# Execute workload script
###############################################################################

echo "============================================================"
echo " Running workload: $WORKLOAD"
echo " Script          : $SCRIPT"
echo " Arguments       : $@"
echo "============================================================"

exec "$SCRIPT" "$@"
