# distutils: language = c++


import cython

from libc.stdint cimport uint8_t, uint32_t, int64_t
cimport numpy as np

from ChunkCpp cimport ChunkCpp


cdef class Chunk:
	cdef int64_t x, z
	cdef ChunkCpp* chunk
	cdef np.ndarray blocks

	@staticmethod
	cdef Chunk create(ChunkCpp* chunkCpp)