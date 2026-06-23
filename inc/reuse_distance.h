#ifndef REUSE_DISTANCE_H
#define REUSE_DISTANCE_H

#include <cstdint>

void reuse_distance_access(uint32_t cpu, uint64_t addr, uint8_t type);
void reuse_distance_clear();
void reuse_distance_final_stats();

#endif