cimport numpy as np
import numpy as np

from Blocks import Blocks
import itertools as it
import math

import cython


cdef int CHUNK_SIZE_X = 16
cdef int CHUNK_SIZE_Y = 128
cdef int CHUNK_SIZE_Z = 16

class Chunk:
	# cdef public np.ndarray[np.int_t, ndim=3] blocks
	# cdef public int x, y
	# cdef public np.int_t[:, :, :] blocks
	# @cython.boundscheck(False) # turn off bounds-checking for entire function
	# @cython.wraparound(False)  # turn off negative index wrapping for entire function
	def __init__(self, int x_, int z_):
		self.x = x_
		self.z = z_
		# cdef np.ndarray[np.int_t, ndim=3] self.blocks
		self.blocks = np.zeros((CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z), dtype=np.int8)
		# self.blocks = np.empty((CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z), dtype=np.int8)

		cdef int xx, yy, zz
		for xx in range(CHUNK_SIZE_X):
			for yy in range(CHUNK_SIZE_Y):
				for zz in range(CHUNK_SIZE_Z):
		# for x, y, z in it.product(range(CHUNK_SIZE_X), range(CHUNK_SIZE_Y), range(CHUNK_SIZE_Z)):
					if yy < 50 + math.sin(((self.x*CHUNK_SIZE_X + xx) + 2 * (self.z * CHUNK_SIZE_Z + zz)) / 10) * 5:
						# pass
						self.blocks[xx][yy][zz] = Blocks.Dirt

	def getMesh(self, nx, px, nz, pz): # parameters: neighporing chunks (negative x, positive x, negative z, positive z)
		vertices = []
		indices = []
		numVerts = 0

		cdef int x, y, z
		for x in range(CHUNK_SIZE_X):
			for y in range(CHUNK_SIZE_Y):
				for z in range(CHUNK_SIZE_Z):
					# top face:
					if self.blocks[x][y][z] != Blocks.Air and (y >= CHUNK_SIZE_Y-1 or self.blocks[x][y+1][z]==Blocks.Air):
						vertices += [x,   y+1, z,   0, 0]
						vertices += [x+1, y+1, z,   0, 1]
						vertices += [x  , y+1, z+1, 1, 0]
						vertices += [x+1, y+1, z+1, 1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

					# bottom face:
					if self.blocks[x][y][z] != Blocks.Air and (y <= 0 or self.blocks[x][y-1][z]==Blocks.Air):
						vertices += [x,   y, z+1, 0, 0]
						vertices += [x+1, y, z+1, 0, 1]
						vertices += [x  , y, z,   1, 0]
						vertices += [x+1, y, z,   1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

					# pz face:
					if self.blocks[x][y][z] != Blocks.Air and (z >= CHUNK_SIZE_Z-1 or self.blocks[x][y][z+1]==Blocks.Air):
						vertices += [x,   y+1, z+1, 0, 0]
						vertices += [x+1, y+1, z+1, 0, 1]
						vertices += [x  , y,   z+1, 1, 0]
						vertices += [x+1, y,   z+1, 1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

					# nz face:
					if self.blocks[x][y][z] != Blocks.Air and (z <= 0 or self.blocks[x][y][z-1]==Blocks.Air):
						vertices += [x+1, y+1, z, 0, 0]
						vertices += [x,   y+1, z, 0, 1]
						vertices += [x+1, y,   z, 1, 0]
						vertices += [x,   y,   z, 1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

					# nx face:
					if self.blocks[x][y][z] != Blocks.Air and (x >= CHUNK_SIZE_X-1 or self.blocks[x+1][y][z]==Blocks.Air):
						vertices += [x+1, y+1, z+1, 0, 0]
						vertices += [x+1, y+1, z,   0, 1]
						vertices += [x+1, y,   z+1, 1, 0]
						vertices += [x+1, y,   z,   1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

					# px face:
					if self.blocks[x][y][z] != Blocks.Air and (x <= 0 or self.blocks[x-1][y][z]==Blocks.Air):
						vertices += [x, y+1, z,   0, 0]
						vertices += [x, y+1, z+1, 0, 1]
						vertices += [x, y,   z,   1, 0]
						vertices += [x, y,   z+1, 1, 1]
						indices += [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
						numVerts += 4

		return vertices, indices
		# return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)