# distutils: language = c++

import cython

cimport numpy as np
import numpy as np

from libc.stdint cimport uint8_t, uint32_t, int64_t
from libcpp.vector cimport vector

from constants import *

cdef extern from "ChunkCpp.hpp":
	cdef cppclass ChunkCpp:
		ChunkCpp() except +
		ChunkCpp(ChunkCpp&) except +
		ChunkCpp(int64_t, int64_t) except +
		void* getBuffer() nogil
		void generate() nogil
		void generateMesh() nogil

		# @staticmethod
		# vector[float] getMesh() nogil
		# vector[uint32_t] getIndices(size_t) nogil
		float* getVertices() nogil
		uint32_t* getIndices(size_t) nogil
		size_t numVertices() nogil
		size_t numIndices() nogil