#!/bin/bash


repl_policies=("lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay" "lru" "srrip" "drrip" "hawkeye" "ship" "ship++" "mockingjay")


if [ "$#" -eq 4 ]; then
    ./build_champsim.sh hashed_perceptron no $1 $2 no no no no lru lru lru $3 $4 lru lru lru 1 no

elif [ "$#" -eq 2 ] ; then
    N=${3:-1}
    for (( j=N; j<=14; j++ )); do
        if (( j < 8 )); then
            ./build_champsim.sh hashed_perceptron no $1 $2 no no no no lru lru lru lru "${repl_policies[$((j-1))]}" lru lru lru 1 no
        else
            ./build_champsim.sh hashed_perceptron no $1 $2 no no no no lru lru lru srrip "${repl_policies[$((j-1))]}" lru lru lru 1 no
        fi
    done

elif [ "$#" -eq 3 ] ; then
    j=$3
    if (( j < 8 )); then
        ./build_champsim.sh hashed_perceptron no $1 $2 no no no no lru lru lru lru "${repl_policies[$((j-1))]}" lru lru lru 1 no
    else
        ./build_champsim.sh hashed_perceptron no $1 $2 no no no no lru lru lru srrip "${repl_policies[$((j-1))]}" lru lru lru 1 no
    fi
    

else
    echo "Invalid number of input"
    echo "U can Either give 4 inputs or 2 inputs"
    echo
    echo "Usage of 4 inputs: <L1 Prefetcher> <L2 Prefetcher> <L2 Replacement Policy> <LLC Replacement Policy> "
    echo "./build.sh berti spp lru srrip"
    echo
    echo "Usage of 2 inputs:  <L1 Prefetcher> <L2 Prefetcher> "
    echo "./build.sh berti spp "
    echo
fi
