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

    int64_t access(uint64_t line_addr, uint32_t num_set, uint32_t num_way)
    {
        uint32_t set = line_addr % num_set;
        SetState &set_state = set_states[set];

        access_count++;

        auto it = set_state.line_position.find(line_addr);

        // First time this line is accessed: cold miss
        if (it == set_state.line_position.end()) {
            cold_count++;

            set_state.lru_stack.push_front(line_addr);
            set_state.line_position[line_addr] = set_state.lru_stack.begin();
            return COLD_MISS_RD;
        }

        int64_t rd = get_reuse_distance(set_state, line_addr);
        add_bin(rd, num_way);

        set_state.lru_stack.splice(set_state.lru_stack.begin(),
                                   set_state.lru_stack,
                                   it->second);
        it->second = set_state.lru_stack.begin();

        return rd;
    }

    void add_bin_counts(uint64_t bins[3]) const
    {
        bins[0] += bin_counts[0];
        bins[1] += bin_counts[1];
        bins[2] += bin_counts[2];
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
        std::list<uint64_t> lru_stack;
        std::unordered_map<uint64_t, std::list<uint64_t>::iterator> line_position;
    };

    int64_t get_reuse_distance(const SetState &set_state, uint64_t line_addr) const
    {
        int64_t rd = 0;

        for (auto it = set_state.lru_stack.begin();
             it != set_state.lru_stack.end() && rd < MID_REUSE_LIMIT;
             ++it, ++rd) {
            if (*it == line_addr)
                return rd;
        }

        return MID_REUSE_LIMIT;
    }

    void add_bin(int64_t rd, uint32_t num_way)
    {
        if (rd < 0)
            return;

        if (rd < num_way)
            bin_counts[0]++;
        else if (rd < MID_REUSE_LIMIT)
            bin_counts[1]++;
        else
            bin_counts[2]++;
    }

    // set index -> state of that set
    std::unordered_map<uint32_t, SetState> set_states;
    uint64_t bin_counts[3] = {0, 0, 0};
};

static ReuseDistanceTracker l1d_tracker[NUM_CPUS];
static ReuseDistanceTracker l2c_tracker[NUM_CPUS];

static void record_access(ReuseDistanceTracker tracker[], uint32_t cpu, uint64_t addr, uint8_t type, uint32_t num_set, uint32_t num_way)
{
    if (type == PREFETCH)
        return;

    uint64_t line_addr = addr >> LOG2_BLOCK_SIZE;
    tracker[cpu].access(line_addr, num_set, num_way);
}

static void print_bins(const char *name,
                       const char *way_name,
                       const uint64_t bins[3])
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
    record_access(l1d_tracker, cpu, addr, type, L1D_SET, L1D_WAY);
}

void reuse_distance_l2c_access(uint32_t cpu, uint64_t addr, uint8_t type)
{
    record_access(l2c_tracker, cpu, addr, type, L2C_SET, L2C_WAY);
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
        l1d_tracker[cpu].add_bin_counts(l1d_bins);
        l2c_tracker[cpu].add_bin_counts(l2c_bins);
    }

    print_bins("L1D", "L1D_WAY", l1d_bins);
    print_bins("L2C", "L2C_WAY", l2c_bins);
}
