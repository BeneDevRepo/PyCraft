import numpy as np

from  OpenGL.GL import *
from  OpenGL.arrays.numbers import NumberHandler as NH # used to pass number references to pyopengl

from constants import *
from Chunk import Chunk
from ChunkWorker import ChunkWorker

import time
from collections import defaultdict



class World:
	def __init__(self):
		self.chunks = {}
		self.meshes = {}

		self.numWorkers = 1
		self.workers = []
		self.requested = defaultdict(lambda: False)
		self.newChunks = []
		
		for i in range(self.numWorkers):
			worker = ChunkWorker()
			worker.start()
			self.workers.append(worker)
			# self.workers[0].getLoaded()
	
	def shutdown(self):
		for i in range(self.numWorkers):
			self.workers[i].stop()

	def createBuffers():
		# Create Vertex Array Object:
		vao = GLuint(-1)
		glCreateVertexArrays(1, NH().dataPointer(vao))

		# Create vertex buffer:
		vbo = GLuint(-1)
		glCreateBuffers(1, NH().dataPointer(vbo))

		# Create vertex buffer:
		ebo = GLuint(-1)
		glCreateBuffers(1, NH().dataPointer(ebo))

		# link vao, vbo and ebo
		glVertexArrayVertexBuffer(vao, 0, vbo, 0, FLOATS_PER_VERTEX * 4) # vao, bindIndex, buffer, offset, stride
		glVertexArrayElementBuffer(vao, ebo) # vao, buffer

		# configure vertex attributes:
		glEnableVertexArrayAttrib(vao,  0)
		glVertexArrayAttribFormat(vao,  0, FLOATS_PER_POSITION, GL_FLOAT, False, 0) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(vao, 0, 0)

		glVertexArrayAttribFormat(vao, 1, FLOATS_PER_NORMAL, GL_FLOAT, False, (FLOATS_PER_POSITION) * 4) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(vao, 1, 0) # vao, attribIndex, bindingIndex
		glEnableVertexArrayAttrib(vao, 1) # vao, attribIndex

		glVertexArrayAttribFormat(vao, 2, FLOATS_PER_UV, GL_FLOAT, False, (FLOATS_PER_POSITION + FLOATS_PER_NORMAL) * 4) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(vao, 2, 0) # vao, attribIndex, bindingIndex
		glEnableVertexArrayAttrib(vao, 2) # vao, attribIndex

		glVertexArrayAttribIFormat(vao, 3, FLOATS_PER_EXTRA, GL_UNSIGNED_INT, (FLOATS_PER_POSITION + FLOATS_PER_NORMAL + FLOATS_PER_UV) * 4) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(vao, 3, 0) # vao, attribIndex, bindingIndex
		glEnableVertexArrayAttrib(vao, 3) # vao, attribIndex

		return (vao, vbo, ebo)


	def requestChunk(self, chunkPos):
		if chunkPos not in self.chunks and not self.requested[chunkPos]:
			self.workers[0].requestChunks(chunkPos)
			self.requested[chunkPos] = True
			return True
		return False

	def syncChunks(self):
		MAX_LOADS_PER_FRAME = 5
		numLoaded = 0

		self.newChunks += self.workers[0].getLoaded()
		# for newChunk in self.newChunks:
		for i in range(len(self.newChunks)):

			newChunk = self.newChunks.pop()
			chunkPos = newChunk.getPos()

			if chunkPos in self.requested:
				self.requested[chunkPos] = False
				self.chunks[chunkPos] = newChunk

				# create chunk mesh:
				vertices, indices = self.chunks[chunkPos].getMesh(None, None, None, None)

				vao, vbo, ebo = World.createBuffers()

				self.meshes[chunkPos] = (vao, vbo, ebo, len(indices))

				# upload vertex + index buffer:
				if len(indices) > 0:
					glNamedBufferStorage(self.meshes[chunkPos][1], len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)
					glNamedBufferStorage(self.meshes[chunkPos][2], len(indices) * 4, indices, GL_DYNAMIC_STORAGE_BIT)
			
			numLoaded += 1
			if numLoaded >= MAX_LOADS_PER_FRAME:
				return

	def loadChunk(self, chunkPos):
		# self.requestChunk(chunkPos)
		# return

		start = time.time_ns()
		# load chunk:
		self.chunks[chunkPos] = Chunk(*chunkPos)

		print("Created chunk in:", (time.time_ns() - start) / (10**6), "ms")

		start = time.time_ns()
		# create chunk mesh:
		# vertices, indices = Chunk(*chunkPos).getMesh(None, None, None, None)
		vertices, indices = self.chunks[chunkPos].getMesh(None, None, None, None)
		# print("Loaded Mesh in:", (time.time_ns() - start) / (10**6), "ms")

		# start = time.time_ns()
		vao, vbo, ebo = World.createBuffers()

		self.meshes[chunkPos] = (vao, vbo, ebo, len(indices))

		# upload vertex + index buffer:
		if len(indices) > 0:
			glNamedBufferStorage(self.meshes[chunkPos][1], len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)
			glNamedBufferStorage(self.meshes[chunkPos][2], len(indices) * 4, indices, GL_DYNAMIC_STORAGE_BIT)
		# print("Uploaded Mesh in:", (time.time_ns() - start) / (10**6), "ms")
		# print()


	def unloadChunk(self, chunkPos):
		self.requested[chunkPos] = False # cancel loading chunk

		# delete if already loaded:
		if chunkPos in self.chunks:
			del self.chunks[chunkPos]

		# delete mesh if present:
		if chunkPos in self.meshes:
			glDeleteVertexArrays(1, NH().dataPointer(self.meshes[chunkPos][0]))
			glDeleteBuffers(1, NH().dataPointer(self.meshes[chunkPos][1]))
			glDeleteBuffers(1, NH().dataPointer(self.meshes[chunkPos][2]))
			del self.meshes[chunkPos]


	def loadChunks(self, pos, viewDist): # pos: [playerX, playerY, playerZ], viewDist: distance in chunks
		start = time.time_ns()

		MAX_LOADS_PER_FRAME = 1
		LIMIT_CHUNK_LOADS = True

		centerChunk = (pos[0]//16, pos[2]//16)

		numCreated = 0
		numDeleted = 0

		chunkPositions = list(self.chunks.keys())
		for chunkPos in chunkPositions:
			d = max(abs(chunkPos[0] - centerChunk[0]), abs(chunkPos[1] - centerChunk[1]))
			if d > viewDist:
				self.unloadChunk(chunkPos)
				# print("Deleted at:", chunkPos)
				numDeleted += 1

		for x in range(-viewDist-2, viewDist+2):
			for z in range(-viewDist-2, viewDist+2):
				chunkPos = (centerChunk[0] + x, centerChunk[1] + z)
				d = max(abs(chunkPos[0] - centerChunk[0]),  abs(chunkPos[1] - centerChunk[1]))
				if d <= viewDist and chunkPos not in self.chunks:
					self.loadChunk(chunkPos)
					numCreated += 1

					# if self.requestChunk(chunkPos):
					# 	numCreated += 1

					# print("Created at:", chunkPos)


					if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break

			if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break
		

		# if numCreated!=0 or numDeleted!=0:
		if time.time_ns() - start > 1_000_000: # more than 1ms
			print("Requested:", numCreated, "Deleted:", numDeleted, "In:", (time.time_ns() - start) / (10**6), "ms")
			# print("Created:", numCreated, "Deleted:", numDeleted, "In:", (time.time_ns() - start) / (10**6), "ms")
		
		start = time.time_ns()
		# self.syncChunks()
		if time.time_ns() - start > 1_000_000: # more than 1ms
			print("Synced in:", (time.time_ns() - start) / (10**6), "ms")