import numpy as np

from Blocks import Blocks
from Chunk import Chunk
import time


class World:
	def __init__(self):
		self.chunks = {}
		# self.meshes = {}

	def loadChunks(self, pos, viewDist): # pos: [playerX, playerY, playerZ], viewDist: distance in chunks
		MAX_LOADS_PER_FRAME = 1
		LIMIT_CHUNK_LOADS = True

		centerChunk = (pos[0]//16, pos[2]//16)

		sq = lambda x: x*x # x -> x^2

		numCreated = 0
		numDeleted = 0

		chunkPositions = list(self.chunks.keys())
		for chunkPos in chunkPositions:
			# d = np.sqrt(sq(chunkPos[0] - centerChunk[0]) + sq(chunkPos[1] - centerChunk[1]))
			d = max(abs(chunkPos[0] - centerChunk[0]), abs(chunkPos[1] - centerChunk[1]))
			if d > viewDist:
				del self.chunks[chunkPos]
				numDeleted += 1

		start = time.time_ns()
		for x in range(-viewDist-2, viewDist+2):
			for z in range(-viewDist-2, viewDist+2):
				chunkPos = (x, z)
				# d = np.sqrt(sq(chunkPos[0] - centerChunk[0]) + sq(chunkPos[1] - centerChunk[1]))
				d = max(abs(chunkPos[0] - centerChunk[0]),  abs(chunkPos[1] - centerChunk[1]))
				if d <= viewDist and chunkPos not in self.chunks:
					self.chunks[chunkPos] = Chunk(x, z)
					numCreated += 1

					if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break

			if LIMIT_CHUNK_LOADS and numCreated >= MAX_LOADS_PER_FRAME:
						break

		if numCreated!=0 or numDeleted!=0:
			print("Created:", numCreated, "Deleted:", numDeleted, "In:", (time.time_ns() - start) / (10**6), "ms")