# distutils: language = c++


import cython

cimport numpy as np
import numpy as np

from libc.stdint cimport uint8_t, uint32_t, int64_t
# from libcpp.vector cimport vector

from ChunkCpp cimport ChunkCpp
from constants import *


cdef class Chunk:
	# cdef int64_t x, z
	# cdef ChunkCpp* chunk
	# cdef np.ndarray blocks

	# def __cinit__(self):
	# 	pass
	# def __init__(self):
	# 	pass

	def __init__(self, x, z):
		self.x = x
		self.z = z
		self.chunk = new ChunkCpp(x, z)
		self.blocks = np.asarray(<uint8_t[:CHUNK_SIZE_X, :CHUNK_SIZE_Y, :CHUNK_SIZE_Z]>self.chunk.getBuffer())
		self.chunk.generate()

	def __dealloc__(self):
		del self.chunk

	@cython.nogil
	@staticmethod
	cdef Chunk create(ChunkCpp* chunkCpp):
		cdef Chunk obj = Chunk.__new__(Chunk)
		obj.x = chunkCpp.getX()
		obj.z = chunkCpp.getZ()
		obj.chunk = chunkCpp
		obj.blocks = np.asarray(<uint8_t[:CHUNK_SIZE_X, :CHUNK_SIZE_Y, :CHUNK_SIZE_Z]>chunkCpp.getBuffer())
		return obj

	def getPos(self):
		return (self.x, self.z)
	
	def getBlocks(self):
		return self.blocks
	
	def generateMesh(self, nx, px, nz, pz):
		self.chunk.generateMesh()
		
		
	@cython.cdivision(True)     # Deactivate division by 0 checking.
	def getMesh(self): # parameters: neighporing chunks (negative x, positive x, negative z, positive z)

		cdef float* verts = self.chunk.getVertices()
		cdef uint32_t* inds = self.chunk.getIndices()

		cdef int numVerts = self.chunk.numVertices()
		cdef int numInds = self.chunk.numIndices()
		# cdef int numQuads = numInds // 6

		# prevent 0-size errors
		if numVerts == 0:
			return np.empty((0)), np.empty((0))

		# cdef vector[uint32_t] inds = self.chunk.getIndices(numQuads)

		# cdef np.ndarray va = np.ascontiguousarray(verts, dtype=np.float32)
		# cdef np.ndarray ia = np.ascontiguousarray(inds, dtype=np.uint32)
		cdef np.ndarray va = np.asarray(<np.float32_t[:numVerts]>verts, dtype=np.float32)
		cdef np.ndarray ia = np.asarray(<np.uint32_t[:numInds]>inds, dtype=np.uint32)

		return va, ia