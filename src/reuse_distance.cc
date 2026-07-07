#include "reuse_distance.h"
#include "cache.h"
#include "memory_class.h"

#include <cstdint>
#include <iostream>
#include <list>
#include <unordered_map>

static const int64_t COLD_MISS_RD = -1;
static const uint32_t MID_REUSE_LIMIT = 32;

class ReuseDistanceTracker {
  public:
    uint64_t access_count = 0;
    uint64_t cold_count = 0;

    int64_t access(uint64_t line_addr)
    {
        uint32_t set = line_addr % num_set;
        SetState &set_state = set_states[set];

        access_count++;

        auto it = set_state.line_position.find(line_addr);

        auto it = set_state.last_access_time.find(line_addr);
        if (it == set_state.last_access_time.end()) {
            cold_count++;
            set_state.last_access_time[line_addr] = set_state.access_count;
            set_state.access_order.insert(std::make_pair(set_state.access_count, line_addr));
            reuse_distance_frequency[line_addr][-1]++;
            return -1;
        }

        uint64_t old_time = it->second;
        uint64_t older_or_equal = set_state.access_order.order_of_key(std::make_pair(old_time, UINT64_MAX));
        int64_t rd = static_cast<int64_t>(set_state.access_order.size() - older_or_equal);

        reuse_distance_frequency[line_addr][rd]++;
        set_state.access_order.erase(std::make_pair(old_time, line_addr));

        it->second = set_state.access_count;
        set_state.access_order.insert(std::make_pair(set_state.access_count, line_addr));

        return rd;
    }

    void print_stats(uint32_t cpu) const
    {
        std::cout << "CPU " << cpu << " reuse accesses: " << access_count
                  << " cold: " << cold_count << std::endl;
        std::cout << "CPU " << cpu << " reuse distance frequency table" << std::endl;

        for (const auto &addr_entry : reuse_distance_frequency) {
            const auto &distance_counts = addr_entry.second;
            bool was_reused = false;

            for (const auto &rd_entry : distance_counts) {
                if (rd_entry.first != -1) {
                    was_reused = true;
                    break;
                }
            }

            if (!was_reused)
                continue;

            uint64_t line_addr = addr_entry.first;
            uint64_t byte_addr = line_addr << LOG2_BLOCK_SIZE;

            std::cout << "Address: 0x" << std::hex << byte_addr << std::dec << std::endl;
            std::cout << "reuse_distance,frequency" << std::endl;

            for (const auto &rd_entry : distance_counts) {
                if (rd_entry.first == -1)
                    continue;

                std::cout << rd_entry.first << "," << rd_entry.second << std::endl;
            }
        }
    }

    void add_bin_counts(uint64_t bins[3]) const
    {
        for (const auto &addr_entry : reuse_distance_frequency) {
            for (const auto &rd_entry : addr_entry.second) {
                int64_t rd = rd_entry.first;

                if (rd < 0)
                    continue;
                else if (rd < L1D_WAY)
                    bins[0] += rd_entry.second;
                else if (rd < 32)
                    bins[1] += rd_entry.second;
                else
                    bins[2] += rd_entry.second;
            }
        }
    }

    void clear()
    {
        access_count = 0;
        cold_count = 0;
        bin_counts[0] = 0;
        bin_counts[1] = 0;
        bin_counts[2] = 0;
        set_states.clear();
    }

  private:
    struct SetState {
        uint64_t access_count = 0;
        std::unordered_map<uint64_t, uint64_t> last_access_time;
        OrderedAccessSet access_order;
    };

    std::unordered_map<uint32_t, SetState> set_states;
    std::map<uint64_t, std::map<int64_t, uint64_t>> reuse_distance_frequency;
};

static ReuseDistanceTracker l1d_tracker[NUM_CPUS];
static ReuseDistanceTracker l2c_tracker[NUM_CPUS];

void reuse_distance_access(uint32_t cpu, uint64_t addr, uint8_t type)
{
    if (type == PREFETCH)
        return;

    uint64_t line_addr = addr >> LOG2_BLOCK_SIZE;
    tracker[cpu].access(line_addr);
}

void reuse_distance_clear()
{
    for (uint32_t cpu = 0; cpu < NUM_CPUS; cpu++) {
        l1d_tracker[cpu].clear();
        l2c_tracker[cpu].clear();
    }
}

void reuse_distance_final_stats()
{
    uint64_t l1d_bins[3] = {0, 0, 0};
    uint64_t l2c_bins[3] = {0, 0, 0};

    for (uint32_t cpu = 0; cpu < NUM_CPUS; cpu++) {
        //tracker[cpu].print_stats(cpu);
        tracker[cpu].add_bin_counts(bins);
    }

    print_bins("L1D", "L1D_WAY", l1d_bins);
    print_bins("L2C", "L2C_WAY", l2c_bins);
}