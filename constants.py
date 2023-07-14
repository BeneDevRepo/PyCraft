

CHUNK_SIZE_X = 16
CHUNK_SIZE_Y = 256
CHUNK_SIZE_Z = 16

FLOATS_PER_POSITION = 3
FLOATS_PER_NORMAL = 3
FLOATS_PER_UV = 2
FLOATS_PER_EXTRA = 1
FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_NORMAL + FLOATS_PER_UV + FLOATS_PER_EXTRA


# Block types (also defined in ChunkBuilder.hpp)
class Blocks:
    Air = 0
    Stone = 1
    Dirt = 2
    Grass = 3
    Snow = 4

    Water = 20