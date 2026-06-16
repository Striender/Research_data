#include <unordered_map>
#include "ooo_cpu.h"
#include <stack>

struct loopBf_entry
{
    int trip_count = 0;
    uint64_t targetAddress = 0;
    int non_speculatie_counter = 0;
    unordered_map<uint64_t, int> path_trip_counts;
    unordered_map<uint64_t, unordered_map<int, int>> path_trip_count_occurrences;
    uint64_t ifelse_PC = 0;
    uint64_t taken_path = 0;
    int confidence = 0;
    int instance = 0;
    int loop_exit = 0;
    uint64_t combined_hash = 0;
    bool active_loop = true;
    int extra_pf = 0;   //prefetchs issued after the loop has completed
     //total prefetches issued after loop completion
    uint64_t pf_issued = 0;
};

/*
struct ActiveLoop
{
    uint64_t pc;
    uint64_t bitstream;
    int trip_count;
};
extern stack<ActiveLoop> active_loops;*/

extern unordered_map<uint64_t, loopBf_entry> loopBuffer;
extern uint64_t total_extra_pf;
extern uint64_t total_prefetches;

