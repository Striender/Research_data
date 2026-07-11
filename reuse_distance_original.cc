#include "cache.h"
#include "reuse_distance.h"
#include "memory_class.h"

#include <cstdint>
#include <iostream>
#include <map>
#include <unordered_map>
#include <utility>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

using __gnu_pbds::null_type;
using __gnu_pbds::rb_tree_tag;
using __gnu_pbds::tree;
using __gnu_pbds::tree_order_statistics_node_update;

static const int64_t COLD_MISS_RD = -1;
static const uint32_t MID_REUSE_LIMIT = 32;

class ReuseDistanceTracker {
  public:
    uint64_t access_count = 0;
    uint64_t cold_count = 0;

    int64_t access(uint64_t line_addr, uint32_t num_set)
    {
        uint32_t set = line_addr % num_set;
        SetState &set_state = set_states[set];

        access_count++;
        set_state.access_count++;

        auto it = set_state.last_access_time.find(line_addr);
        if (it == set_state.last_access_time.end()) {
            cold_count++;
            set_state.last_access_time[line_addr] = set_state.access_count;
            set_state.access_order.insert(std::make_pair(set_state.access_count, line_addr));
            reuse_distance_frequency[line_addr][COLD_MISS_RD]++;
            return COLD_MISS_RD;
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

    void add_bin_counts(uint64_t bins[3], uint32_t num_way) const
    {
        for (const auto &addr_entry : reuse_distance_frequency) {
            for (const auto &rd_entry : addr_entry.second) {
                int64_t rd = rd_entry.first;

                if (rd < 0)
                    continue;

                if (rd < num_way)
                    bins[0] += rd_entry.second;
                else if (rd < MID_REUSE_LIMIT)
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
        set_states.clear();
        reuse_distance_frequency.clear();
    }

  private:
    using AccessKey = std::pair<uint64_t, uint64_t>;
    using OrderedAccessSet = tree<AccessKey, null_type, std::less<AccessKey>,
                                  rb_tree_tag, tree_order_statistics_node_update>;

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

static void record_access(ReuseDistanceTracker tracker[], uint32_t cpu,
                          uint64_t addr, uint8_t type, uint32_t num_set)
{
    if (type == PREFETCH)
        return;

    uint64_t line_addr = addr >> LOG2_BLOCK_SIZE;
    tracker[cpu].access(line_addr, num_set);
}

static void print_bins(const char *name, const char *way_name, const uint64_t bins[3])
{
    std::cout << "==============================================" << std::endl;
    std::cout << name << " reuse distance bin frequency table" << std::endl;
    std::cout << "reuse_distance_bin,frequency" << std::endl;
    std::cout << "short[0-" << way_name << ")," << bins[0] << std::endl;
    std::cout << "mid[" << way_name << "-32)," << bins[1] << std::endl;
    std::cout << "long[32+]," << bins[2] << std::endl;
}

void reuse_distance_access(uint32_t cpu, uint64_t addr, uint8_t type)
{
    record_access(l1d_tracker, cpu, addr, type, L1D_SET);
}

void reuse_distance_l2c_access(uint32_t cpu, uint64_t addr, uint8_t type)
{
    record_access(l2c_tracker, cpu, addr, type, L2C_SET);
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
        l1d_tracker[cpu].add_bin_counts(l1d_bins, L1D_WAY);
        l2c_tracker[cpu].add_bin_counts(l2c_bins, L2C_WAY);
    }

    print_bins("L1D", "L1D_WAY", l1d_bins);
    print_bins("L2C", "L2C_WAY", l2c_bins);
}
