#include "cache.h"
#include <unordered_set>
#include <cassert>

using namespace std;

/* ===============================
   POLLUTION TRACKING @ LLC
   =============================== */

// Demand-resident lines in LLC
static unordered_set<uint64_t> llc_demand_resident;

// Lines evicted by prefetch
static unordered_set<uint64_t> llc_evicted_by_prefetch;

// Pollution counter
static uint64_t llc_pollution_count = 0;

/* ===============================
   INITIALIZATION
   =============================== */

void CACHE::llc_initialize_replacement()
{
    cout << NAME << " has LRU replacement policy with pollution tracking" << endl;

    llc_demand_resident.clear();
    llc_evicted_by_prefetch.clear();
    llc_pollution_count = 0;
}

/* ===============================
   FIND VICTIM (LRU)
   =============================== */

uint32_t CACHE::llc_find_victim(uint32_t cpu, uint64_t instr_id,
                                uint32_t set, const BLOCK *current_set,
                                uint64_t ip, uint64_t full_addr, uint32_t type)
{
    return lru_victim(cpu, instr_id, set, current_set, ip, full_addr, type);
}

/* ===============================
   UPDATE REPLACEMENT STATE
   =============================== */

void CACHE::llc_update_replacement_state(uint32_t cpu, uint32_t set,
                                         uint32_t way, uint64_t full_addr,
                                         uint64_t ip, uint64_t victim_addr,
                                         uint32_t type, uint8_t hit)
{
    if ((type == WRITEBACK) && ip)
        assert(0);

    bool is_prefetch = (type == PREFETCH);

    bool is_demand = (type == LOAD);

    uint64_t line_addr = full_addr >> LOG2_BLOCK_SIZE;

    /* ---------- Eviction handling ---------- */
    if (!hit && victim_addr != 0)
    {
        uint64_t victim_line = victim_addr >> LOG2_BLOCK_SIZE;

        auto it = llc_demand_resident.find(victim_line);
        if (it != llc_demand_resident.end())
        {
            if (is_prefetch)
                llc_evicted_by_prefetch.insert(victim_line);
            llc_demand_resident.erase(it);
        }
    }

    /* ---------- Demand miss ---------- */
    if (!hit && is_demand)
    {
        auto it2 = llc_evicted_by_prefetch.find(line_addr);
        if (it2 != llc_evicted_by_prefetch.end())
        {
            llc_pollution_count++;
            llc_evicted_by_prefetch.erase(it2);
        }
        //llc_demand_resident.insert(line_addr);
    }

    /* ---------- Demand hit ---------- */
    if (hit && is_demand)
        llc_demand_resident.insert(line_addr);

    /* ---------- Original LRU ---------- */
    if (hit && type == WRITEBACK)
        return;

    lru_update(set, way);
}

/* ===============================
   FINAL STATS
   =============================== */

void CACHE::llc_replacement_final_stats()
{
    cout << "================ LLC LRU Pollution Stats ================" << endl;
    cout << "Total pollution count in LLC: " << llc_pollution_count << endl;
    cout << "=========================================================" << endl;
}
