if [ $# -ne 4 ]; then
    echo "Usage: $0 <L1 Prefetcher> <L2 Prefetcher> <L2 Replacement Policy> <LLC Replacement Policy> "
    exit 1
fi

./build_champsim.sh bimodal no $1 $2 no no no no lru lru lru $3 $4 lru lru lru 1 no 