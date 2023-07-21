# distutils: language = c++


import cython

from libcpp cimport bool
from libc.stdint cimport uint8_t, uint32_t, int64_t
from libcpp.vector cimport vector

from ChunkCpp cimport ChunkCpp
from Chunk cimport Chunk

import threading as th
# import time

cimport openmp


cdef class ChunkWorker:
	cdef bool shouldStop
	# cdef object mutex
	cdef openmp.omp_lock_t mutex
	cdef object thread
	cdef object event

	cdef vector[int64_t] requested
	cdef vector[ChunkCpp*] loaded

	def __init__(self):
		self.shouldStop = False # only accassible while hilding mutex
		# self.mutex = th.Lock()
		openmp.omp_init_lock(&self.mutex)
		self.thread = th.Thread(target=self.run)
		self.event = th.Event()

	def start(self):
		self.thread.start()

	def stop(self):
		# with self.mutex:
		# 	self.shouldStop = True

		openmp.omp_set_lock(&self.mutex)
		self.shouldStop = True
		openmp.omp_unset_lock(&self.mutex)
		
		self.event.set()
		self.thread.join()


	@cython.boundscheck(False)
	@cython.wraparound(False)
	def requestChunks(self, chunkPositions):
		cdef int64_t val
		# with self.mutex:
		# with nogil, cython.boundscheck(False), cython.wraparound(False):
		openmp.omp_set_lock(&self.mutex)
		for val in chunkPositions:
			self.requested.push_back(val)
		openmp.omp_unset_lock(&self.mutex)
		self.event.set()



	@cython.boundscheck(False)
	@cython.wraparound(False)
	def getLoaded(self):
		cdef list chunks = list()
		cdef ChunkCpp* chunkCpp

		# with self.mutex:
		openmp.omp_set_lock(&self.mutex)
		# for chunkCpp in self.loaded:
		# 	chunks.append(Chunk.create(chunkCpp))
		# self.loaded.clear()

		for i in range(min(1, self.loaded.size())):
			chunkCpp = self.loaded.back()
			self.loaded.pop_back()
			chunks.append(Chunk.create(chunkCpp))

		openmp.omp_unset_lock(&self.mutex)

		return chunks



	@cython.boundscheck(False)
	@cython.wraparound(False)
	def run(self):
		cdef vector[int64_t] req
		# cdef vector[ChunkCpp*] created

		while True:
			# with self.mutex:
			# 	if self.shouldStop:
			# 		break

			# 	req = self.requested
			# 	self.requested.clear()
			openmp.omp_set_lock(&self.mutex)
			if self.shouldStop:
				break

			if self.requested.size() == 0:
				openmp.omp_unset_lock(&self.mutex)
				# time.sleep(1.)
				if self.event.wait(1):
					self.event.clear()
				continue

			# req = self.requested
			# self.requested.clear()

			req.clear()

			for i in range(min(5, self.requested.size()//2)):
				req.push_back(self.requested.at(self.requested.size() - 2))
				req.push_back(self.requested.at(self.requested.size() - 1))
				self.requested.pop_back()
				self.requested.pop_back()
			openmp.omp_unset_lock(&self.mutex)

			created = self.run_c(req)
			# self.run_c(req)

			# with self.mutex:
			# 	for chunk in created:
			# 		self.loaded.push_back(chunk)
			openmp.omp_set_lock(&self.mutex)
			for chunk in created:
				self.loaded.push_back(chunk)
				# time.sleep(.01)
			openmp.omp_unset_lock(&self.mutex)

			# time.sleep(.1)
			if self.event.wait(.01):
				self.event.clear()


	@cython.nogil
	cdef vector[ChunkCpp*] run_c(self, vector[int64_t] requested):
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