#include "cache.h"
#include <unordered_set>

unordered_set<uint64_t> l1d_demand_resident;
unordered_set<uint64_t> l1d_evicted_by_prefetch;
uint64_t l1d_pollution_count = 0;
int pf = 0;
int evicted = 0;

// initialize replacement state
void CACHE::l1d_initialize_replacement()
{
    cout << NAME << " has LRU replacement policy" << endl;

    l1d_demand_resident.clear();
    l1d_evicted_by_prefetch.clear();
}

// find replacement victim
uint32_t CACHE::l1d_find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    // baseline LRU
    return lru_victim(cpu, instr_id, set, current_set, ip, full_addr, type);
}

// called on every cache hit and cache fill
void CACHE::l1d_update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{

    bool is_prefetched = (type == PREFETCH);
    bool is_demand = (type == LOAD);

    if ((type == WRITEBACK) && ip)
        assert(0);


    uint64_t line_addr = full_addr >> LOG2_BLOCK_SIZE;
    // 1) Handle the victim if this access caused an eviction (on a miss)
    if (!hit && victim_addr != 0)
    {
        uint64_t victim_line = victim_addr >> LOG2_BLOCK_SIZE;

        auto it = l1d_demand_resident.find(victim_line);
        if (it != l1d_demand_resident.end())
        {
            if (is_prefetched)
            {
                l1d_evicted_by_prefetch.insert(victim_line);
            }
            l1d_demand_resident.erase(it);
        }
    }

    if (!hit && is_demand)
    {
        auto it2 = l1d_evicted_by_prefetch.find(line_addr);
        if (it2 != l1d_evicted_by_prefetch.end())
        {
            l1d_pollution_count++;
            l1d_evicted_by_prefetch.erase(it2);
        }
        // If the miss results in an installation in LLC (not bypass), mark as resident demand line
        if (way < LLC_WAY)
        {
            l1d_demand_resident.insert(line_addr);
        }
    }

    // 3) If this is a demand hit in LLC, the line is definitely useful.
    //    Mark it as demand-resident (if not already).
    if (hit && is_demand && way < LLC_WAY)
    {
        l1d_demand_resident.insert(line_addr);
    }

    // uncomment this line to see the LLC accesses
    // cout << "CPU: " << cpu << "  LLC " << setw(9) << TYPE_NAME << " set: " << setw(5) << set << " way: " << setw(2) << way;
    // cout << hex << " paddr: " << setw(12) << paddr << " ip: " << setw(8) << ip << " victim_addr: " << victim_addr << dec << endl;

    // baseline LRU
    if (hit && (type == WRITEBACK)) // writeback hit does not update LRU state
        return;

    return lru_update(set, way);
}

void CACHE::l1d_replacement_final_stats()
{
    cout << "===================== LRU L1D STATS =====================" << endl;
    cout << "Total pollution count in L1D: " << l1d_pollution_count << endl;
    cout << "=========================================================" << endl;
}
