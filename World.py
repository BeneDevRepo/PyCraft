import numpy as np

from  OpenGL.GL import *
from  OpenGL.arrays.numbers import NumberHandler as NH # used to pass number references to pyopengl

from Blocks import Blocks
from Chunk import Chunk
import time


FLOATS_PER_POSITION = 3
FLOATS_PER_NORMAL = 3
FLOATS_PER_UV = 2
FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_NORMAL + FLOATS_PER_UV


class World:
	def __init__(self):
		self.chunks = {}
		self.meshes = {}

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

		# glVertexArrayAttribFormat(vao, 1, FLOATS_PER_UV, GL_FLOAT, False, FLOATS_PER_POSITION * 4) # vao, attribIndex, size, type, normalized, offset
		# glVertexArrayAttribBinding(vao, 1, 0) # vao, attribIndex, bindingIndex
		# glEnableVertexArrayAttrib(vao, 1) # vao, attribIndex

		return (vao, vbo, ebo)


	def loadChunk(self, x, z):
		# load chunk:
		self.chunks[(x, z)] = Chunk(x, z)

		# create chunk mesh:
		vertices, indices = Chunk(x, z).getMesh(None, None, None, None)
		# vertices, indices = np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)

		vao, vbo, ebo = World.createBuffers()

		self.meshes[(x, z)] = (vao, vbo, ebo, len(indices))

		# upload vertex + index buffer:
		glNamedBufferStorage(self.meshes[(x, z)][1], len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)
		glNamedBufferStorage(self.meshes[(x, z)][2], len(indices) * 4, indices, GL_DYNAMIC_STORAGE_BIT)

	def unloadChunk(self, x, z):
		del self.chunks[(x, z)]
		glDeleteVertexArrays(1, NH().dataPointer(self.meshes[(x, z)][0]))
		glDeleteBuffers(1, NH().dataPointer(self.meshes[(x, z)][1]))
		glDeleteBuffers(1, NH().dataPointer(self.meshes[(x, z)][2]))
		del self.meshes[(x, z)]


	def loadChunks(self, pos, viewDist): # pos: [playerX, playerY, playerZ], viewDist: distance in chunks
		MAX_LOADS_PER_FRAME = 1
		LIMIT_CHUNK_LOADS = True

		centerChunk = (pos[0]//16, pos[2]//16)

		# sq = lambda x: x*x # x -> x^2

		numCreated = 0
		numDeleted = 0

		chunkPositions = list(self.chunks.keys())
		for chunkPos in chunkPositions:
			d = max(abs(chunkPos[0] - centerChunk[0]), abs(chunkPos[1] - centerChunk[1]))
			if d > viewDist:
				self.unloadChunk(*chunkPos)
				numDeleted += 1

		start = time.time_ns()
		for x in range(-viewDist-2, viewDist+2):
			for z in range(-viewDist-2, viewDist+2):
				chunkPos = (x, z)
				d = max(abs(chunkPos[0] - centerChunk[0]),  abs(chunkPos[1] - centerChunk[1]))
				if d <= viewDist and chunkPos not in self.chunks:
					self.loadChunk(x, z)

					numCreated += 1

					if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break

			if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break

		if numCreated!=0 or numDeleted!=0:
			print("Created:", numCreated, "Deleted:", numDeleted, "In:", (time.time_ns() - start) / (10**6), "ms")