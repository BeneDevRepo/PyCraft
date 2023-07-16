# distutils: language = c++


import cython

from libcpp cimport bool
from libc.stdint cimport uint8_t, uint32_t, int64_t
from libcpp.vector cimport vector

from ChunkCpp cimport ChunkCpp
# from Chunk import Chunk
from Chunk cimport Chunk

import threading as th



cdef class ChunkWorker:
	cdef bool shouldStop
	cdef object mutex
	cdef object thread
	cdef object event

	cdef vector[int64_t] requested
	cdef vector[ChunkCpp*] loaded

	def __init__(self):
		self.shouldStop = False # only accassible while hilding mutex
		self.mutex = th.Lock()
		self.thread = th.Thread(target=self.run)
		self.event = th.Event()

	def start(self):
		self.thread.start()

	def stop(self):
		with self.mutex:
			self.shouldStop = True
		
		self.event.set()
		self.thread.join()


	def requestChunks(self, chunkPositions):
		cdef int64_t val
		with self.mutex:
			pass
			for val in chunkPositions:
				self.requested.push_back(val)
		# self.event.set()


	def getLoaded(self):
		cdef list chunks = list()
		cdef ChunkCpp* chunkCpp

		with self.mutex:
			for chunkCpp in self.loaded:
				chunks.append(Chunk.create(chunkCpp))

			self.loaded.clear()

		return chunks


	def run(self):
		cdef vector[int64_t] req
		# cdef vector[ChunkCpp*] created

		while True:
			with self.mutex:
				if self.shouldStop:
					break

				req = self.requested
				self.requested.clear()

			created = self.run_c(req)
			# self.run_c(req)

			with self.mutex:
				for chunk in created:
					self.loaded.push_back(chunk)

			if self.event.wait(1):
				self.event.clear()

	@cython.nogil
	cdef vector[ChunkCpp*] run_c(self, vector[int64_t] requested):
		# cdef vector[ChunkCpp*] current # = vector[ChunkCpp*](requested.size())
		cdef vector[ChunkCpp*] currentChunks # = vector[ChunkCpp*](requested.size())
		cdef ChunkCpp* current

		cdef int64_t i, x, y
		for i in range(requested.size() // 2):
			x = requested[i * 2]
			y = requested[i * 2 + 1]

			current = new ChunkCpp(x, y)
			current.generate()

			# with self.mutex:
			# 	self.loaded.push_back(current)

			currentChunks.push_back(current)

		return currentChunks