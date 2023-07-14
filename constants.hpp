#pragma once

#include <cstdint>

static constexpr size_t CHUNK_SIZE_X = 16;
static constexpr size_t CHUNK_SIZE_Y = 256;
static constexpr size_t CHUNK_SIZE_Z = 16;

static constexpr size_t FLOATS_PER_POSITION = 3;
static constexpr size_t FLOATS_PER_NORMAL = 3;
static constexpr size_t FLOATS_PER_UV = 2;
static constexpr size_t FLOATS_PER_EXTRA = 1;
static constexpr size_t FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_NORMAL + FLOATS_PER_UV + FLOATS_PER_EXTRA;

using Block = uint8_t;

static constexpr Block BLOCK_AIR = 0;
static constexpr Block BLOCK_STONE = 1;
static constexpr Block BLOCK_DIRT = 2;
static constexpr Block BLOCK_GRASS = 3;
static constexpr Block BLOCK_SNOW = 4;

static constexpr Block BLOCK_WATER = 20;