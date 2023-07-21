#pragma once

#include <cstdint>
#include <vector>

#include "WorldGen.hpp"


class ChunkCpp {
private:
	int64_t x, z;
	Block blocks[CHUNK_SIZE_X][CHUNK_SIZE_Y][CHUNK_SIZE_Z];

	std::vector<float> vertexBuffer;
	std::vector<uint32_t> indexBuffer;

public:
	inline ChunkCpp(): x(0), z(0), vertexBuffer{}, indexBuffer{} { }

	inline ChunkCpp(const int64_t x, const int64_t z): x(x), z(z), vertexBuffer{}, indexBuffer{} { }

	inline void* getBuffer() {
		return blocks;
	}

	inline int64_t getX() const {
		return x;
	}

	inline int64_t getZ() const {
		return z;
	}

	inline void generate()  {
		for(size_t x = 0; x < CHUNK_SIZE_X; x++) {
			for(size_t y = 0; y < CHUNK_SIZE_Y; y++) {
				for(size_t z = 0; z < CHUNK_SIZE_Z; z++) {
					const int64_t ax = this->x * CHUNK_SIZE_X + x;
					const int64_t az = this->z * CHUNK_SIZE_Z + z;

					blocks[x][y][z] = getBlock(ax, y, az);
					// blocks[x][y][z] = y < 60 ? BLOCK_STONE : BLOCK_AIR;
				}
			}
		}
	}

	inline void generateMesh() {
		vertexBuffer.clear();
		indexBuffer.clear();

		const auto emitQuad = [this](const float *const pos, const float *const norm, const Block block) {
				const uint32_t extra = block;

				const float fExtra = *reinterpret_cast<const float*>(&extra);
				
				const float newVerts[] {
					pos[0], pos[1],  pos[2],  norm[0], norm[1], norm[2], 0.f, 0.f, fExtra,
					pos[3], pos[4],  pos[5],  norm[0], norm[1], norm[2], 0.f, 1.f, fExtra,
					pos[6], pos[7],  pos[8],  norm[0], norm[1], norm[2], 1.f, 0.f, fExtra,
					pos[9], pos[10], pos[11], norm[0], norm[1], norm[2], 1.f, 1.f, fExtra
				};


				const uint32_t numVerts = vertexBuffer.size() / FLOATS_PER_VERTEX;
				const uint32_t newInds[] {
					numVerts + 0, numVerts + 1, numVerts + 3,
					numVerts + 0, numVerts + 3, numVerts + 2
				};

				vertexBuffer.insert(vertexBuffer.end(), (float*)newVerts, ((float*)newVerts) + (sizeof(newVerts) / sizeof(float)));
				indexBuffer.insert(indexBuffer.end(), newInds, newInds + (sizeof(newInds) / sizeof(uint32_t)));
			};


		const auto isAir = [](const Block block) {
				return block == BLOCK_AIR;
			};

		const auto isTranslucent = [](const Block block) {
				return block == BLOCK_AIR || block == BLOCK_WATER;
			};


		for(size_t x = 0; x < CHUNK_SIZE_X; x++) {
			for(size_t y = 0; y < CHUNK_SIZE_Y; y++) {
				for(size_t z = 0; z < CHUNK_SIZE_Z; z++) {
					if(isAir(blocks[x][y][z])) continue;

					// top face:
					if(y >= CHUNK_SIZE_Y-1 || (blocks[x][y][z] != blocks[x][y+1][z])&&isTranslucent(blocks[x][y+1][z])) {
						const float normal[] { 0., 1., 0. };
						const float vertices[] {
							x,   y+1, z,
							x+1, y+1, z,
							x  , y+1, z+1,
							x+1, y+1, z+1
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}

					// bottom face:
					if(y <= 0 || (blocks[x][y][z] != blocks[x][y-1][z]) && isTranslucent(blocks[x][y-1][z])) {
						const float normal[] { 0., -1., 0. };
						const float vertices[] {
							x,   y, z+1,
							x+1, y, z+1,
							x  , y, z,  
							x+1, y, z
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}

					// pz face:
					if(z >= CHUNK_SIZE_Z-1 || (blocks[x][y][z] != blocks[x][y][z+1]) && isTranslucent(blocks[x][y][z+1])) {
						const float normal[] { 0., 0., 1. };
						const float vertices[] {
							x,   y+1, z+1,
							x+1, y+1, z+1,
							x  , y,   z+1,
							x+1, y,   z+1
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}

					// nz face:
					if(z <= 0 || (blocks[x][y][z] != blocks[x][y][z-1]) && isTranslucent(blocks[x][y][z-1])) {
						const float normal[] { 0., 0., -1. };
						const float vertices[] {
							x+1, y+1, z,
							x,   y+1, z,
							x+1, y,   z,
							x,   y,   z
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}

					// px face:
					if(x >= CHUNK_SIZE_X-1 || (blocks[x][y][z] != blocks[x+1][y][z]) && isTranslucent(blocks[x+1][y][z])) {
						const float normal[] { 1., 0., 0. };
						const float vertices[] {
							x+1, y+1, z+1,
							x+1, y+1, z,
							x+1, y,   z+1,
							x+1, y,   z
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}

					// nx face:
					if(x <= 0 || (blocks[x][y][z] != blocks[x-1][y][z]) && isTranslucent(blocks[x-1][y][z])) {
						const float normal[] { -1., 0., 0. };
						const float vertices[] {
							x, y+1, z,
							x, y+1, z+1,
							x, y,   z,
							x, y,   z+1
						};
						emitQuad(vertices, normal, blocks[x][y][z]);
					}
				}
			}
		}
	}

	inline float* getVertices() {
		return vertexBuffer.data();
	}

	inline uint32_t* getIndices() {
		return indexBuffer.data();
	}

	inline size_t numVertices() const {
		return vertexBuffer.size();
	}

	inline size_t numIndices() const {
		return indexBuffer.size();
	}
};