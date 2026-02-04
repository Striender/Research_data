#include "cache.h"
#include <unordered_set>
#include <cassert>

using namespace std;

// Demand-touched lines currently resident in L2
static unordered_set<uint64_t> l2_demand_resident;

// Lines evicted by prefetch
static unordered_set<uint64_t> l2_evicted_by_prefetch;

// Total pollution events
static uint64_t l2_pollution_count = 0;

void CACHE::l2c_initialize_replacement()
{
    cout << NAME << " has LRU replacement policy with pollution tracking" << endl;

    l2_demand_resident.clear();
    l2_evicted_by_prefetch.clear();
    l2_pollution_count = 0;
}

uint32_t CACHE::l2c_find_victim(uint32_t cpu, uint64_t instr_id,
                                uint32_t set, const BLOCK *current_set,
                                uint64_t ip, uint64_t full_addr, uint32_t type)
{
    return lru_victim(cpu, instr_id, set, current_set, ip, full_addr, type);
}

void CACHE::l2c_update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way,
                                         uint64_t full_addr, uint64_t ip,
                                         uint64_t victim_addr, uint32_t type,
                                         uint8_t hit)
{
    if ((type == WRITEBACK) && ip)
        assert(0);

    /* -------------------------------
       POLLUTION LOGIC
       ------------------------------- */

    bool is_prefetch =
        (type == PREFETCH);

    bool is_demand = (type == LOAD);

    uint64_t line_addr = full_addr >> LOG2_BLOCK_SIZE;

    // 1) Handle eviction on miss
    if (!hit && victim_addr != 0)
    {
        uint64_t victim_line = victim_addr >> LOG2_BLOCK_SIZE;

        auto it = l2_demand_resident.find(victim_line);
        if (it != l2_demand_resident.end())
        {
            if (is_prefetch)
            {
                // Prefetch evicted a demand-resident line
                l2_evicted_by_prefetch.insert(victim_line);
            }
            l2_demand_resident.erase(it);
        }
    }

    // 2) Demand miss → pollution check
    if (!hit && is_demand)
    {
        auto it2 = l2_evicted_by_prefetch.find(line_addr);
        if (it2 != l2_evicted_by_prefetch.end())
        {
            l2_pollution_count++;
            l2_evicted_by_prefetch.erase(it2);
        }

        // Line will be installed in L2
        //l2_demand_resident.insert(line_addr);
    }

    // 3) Demand hit → mark as useful
    if (hit && is_demand)
    {
        l2_demand_resident.insert(line_addr);
    }

    /* -------------------------------
       ORIGINAL LRU LOGIC
       ------------------------------- */

    // Writeback hit does not update LRU
    if (hit && type == WRITEBACK)
        return;

    lru_update(set, way);
}

void CACHE::l2c_replacement_final_stats()
{
    cout << "================ L2 LRU Pollution ================" << endl;
    cout << "Total pollution count in L2: " << l2_pollution_count << endl;
    cout << "========================================================" << endl;
}
