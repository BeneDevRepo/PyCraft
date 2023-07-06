cimport numpy as np
import numpy as np

from cpython cimport array
from libc.string cimport memcpy

from Blocks import Blocks
import math

import cython
import time


cdef:
	int CHUNK_SIZE_X = 16
	int CHUNK_SIZE_Y = 128
	int CHUNK_SIZE_Z = 16

	int FLOATS_PER_POSITION = 3
	int FLOATS_PER_NORMAL = 3
	int FLOATS_PER_UV = 2
	int FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_NORMAL + FLOATS_PER_UV

	int TOTAL_BLOCKS = CHUNK_SIZE_X * CHUNK_SIZE_Y * CHUNK_SIZE_Z
	int MAX_FACES = TOTAL_BLOCKS * 3
	int MAX_VERTICES = MAX_FACES * 4
	int MAX_INDICES = MAX_FACES * 6

	# float vertBuffer[MAX_VERTICES * FLOATS_PER_VERTEX]
	# int indBuffer[MAX_INDICES]
	# float vertBuffer[393216 * 5]
	# int indBuffer[589824]
	float[:] vertBuffer = np.empty((MAX_VERTICES * FLOATS_PER_VERTEX), dtype=np.float32)
	int[:] indBuffer = np.empty((MAX_INDICES), dtype=np.int32)
	# vertBuffer = np.empty((MAX_VERTICES * FLOATS_PER_VERTEX), dtype=np.float32)
	# indBuffer = np.empty((MAX_INDICES), dtype=np.int32)
	int numVerts;
	int numInds;


class Chunk:
	@cython.boundscheck(False) # turn off bounds-checking for entire function
	@cython.wraparound(False)  # turn off negative index wrapping for entire function
	def __init__(self, int x_, int z_):
		self.x = x_
		self.z = z_
		# self.blocks = np.zeros((CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z), dtype=np.int8)
		self.blocks = np.empty((CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z), dtype=np.int8)

		cdef:
			int x, y, z

		for x in range(CHUNK_SIZE_X):
			for y in range(CHUNK_SIZE_Y):
				for z in range(CHUNK_SIZE_Z):
		# for x, y, z in it.product(range(CHUNK_SIZE_X), range(CHUNK_SIZE_Y), range(CHUNK_SIZE_Z)):
					if y < 50 + math.sin(((self.x*CHUNK_SIZE_X + x) + 3 * (self.z * CHUNK_SIZE_Z + z)) / 10) * 5:
						# pass
						self.blocks[x][y][z] = Blocks.Dirt
					else:
						self.blocks[x][y][z] = Blocks.Air


	@cython.boundscheck(False)
	@cython.wraparound(False)
	def emitQuad(self, vertices):
		global vertBuffer, indBuffer, numVerts, numInds
		# vertices = np.array(vertices, dtype=np.float32)
		cdef int[6] indices = [numVerts + 0, numVerts + 1, numVerts + 3, numVerts + 0, numVerts + 3, numVerts + 2]
		cdef int i
		for i in range(6):
			indBuffer[numInds + i] = indices[i]
		for i in range(4 * FLOATS_PER_VERTEX):
			vertBuffer[numVerts * FLOATS_PER_VERTEX + i] = vertices[i]

		numVerts += 4
		numInds += 6


	@cython.boundscheck(False)
	@cython.wraparound(False)
	def getMesh(self, nx, px, nz, pz): # parameters: neighporing chunks (negative x, positive x, negative z, positive z)
		global numVerts, numInds
		numVerts = 0
		numInds = 0

		cdef:
			# list vertices = []
			# list indices = []
			# array.array vertices = array.array("f")
			# array.array indices = array.array("l")
			# int numVerts = 0
			# int numInds = 0
			# self.numVerts = 0
			# self.numInds = 0
			int x, y, z
			# float[4 * 5] vertices


		for x in range(CHUNK_SIZE_X):
			for y in range(CHUNK_SIZE_Y):
				for z in range(CHUNK_SIZE_Z):
					# top face:
					if self.blocks[x][y][z] != Blocks.Air and (y >= CHUNK_SIZE_Y-1 or self.blocks[x][y+1][z]==Blocks.Air):
						norm = (0, 1, 0)
						vertices = [
							x,   y+1, z,   *norm, 0, 0,
							x+1, y+1, z,   *norm, 0, 1,
							x  , y+1, z+1, *norm, 1, 0,
							x+1, y+1, z+1, *norm, 1, 1]
						self.emitQuad(vertices)

					# bottom face:
					if self.blocks[x][y][z] != Blocks.Air and (y <= 0 or self.blocks[x][y-1][z]==Blocks.Air):
						norm = (0, -1, 0)
						vertices = [
							x,   y, z+1, *norm, 0, 0,
							x+1, y, z+1, *norm, 0, 1,
							x  , y, z,   *norm, 1, 0,
							x+1, y, z,   *norm, 1, 1]
						self.emitQuad(vertices)

					# pz face:
					if self.blocks[x][y][z] != Blocks.Air and (z >= CHUNK_SIZE_Z-1 or self.blocks[x][y][z+1]==Blocks.Air):
						norm = (0, 0, 1)
						vertices = [
							x,   y+1, z+1, *norm, 0, 0,
							x+1, y+1, z+1, *norm, 0, 1,
							x  , y,   z+1, *norm, 1, 0,
							x+1, y,   z+1, *norm, 1, 1]
						self.emitQuad(vertices)

					# nz face:
					if self.blocks[x][y][z] != Blocks.Air and (z <= 0 or self.blocks[x][y][z-1]==Blocks.Air):
						norm = (0, 0, -1)
						vertices = [
							x+1, y+1, z, *norm, 0, 0,
							x,   y+1, z, *norm, 0, 1,
							x+1, y,   z, *norm, 1, 0,
							x,   y,   z, *norm, 1, 1]
						self.emitQuad(vertices)

					# px face:
					if self.blocks[x][y][z] != Blocks.Air and (x >= CHUNK_SIZE_X-1 or self.blocks[x+1][y][z]==Blocks.Air):
						norm = (1, 0, 0)
						vertices = [
							x+1, y+1, z+1, *norm, 0, 0,
							x+1, y+1, z,   *norm, 0, 1,
							x+1, y,   z+1, *norm, 1, 0,
							x+1, y,   z,   *norm, 1, 1]
						self.emitQuad(vertices)

					# nx face:
					if self.blocks[x][y][z] != Blocks.Air and (x <= 0 or self.blocks[x-1][y][z]==Blocks.Air):
						norm = (-1, 0, 0)
						vertices = [
							x, y+1, z,   *norm, 0, 0,
							x, y+1, z+1, *norm, 0, 1,
							x, y,   z,   *norm, 1, 0,
							x, y,   z+1, *norm, 1, 1]
						self.emitQuad(vertices)

		# return vertBuffer, indBuffer
		return np.array(vertBuffer[:numVerts*FLOATS_PER_VERTEX], dtype=np.float32, copy=True), np.array(indBuffer[:numInds], dtype=np.int32, copy=True)
		# return np.asarray(vertBuffer[:numVerts*FLOATS_PER_VERTEX], dtype=np.float32), np.asarray(indBuffer[:numInds], dtype=np.int32)
		# return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)