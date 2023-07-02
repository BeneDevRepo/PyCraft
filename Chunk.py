import numpy as np

from Blocks import Blocks


class Chunk:
	def __init__(self, x, z):
		self.x = x
		self.z = z
		self.blocks = np.zeros((16, 256, 16), dtype=np.int8)
		for y in range(256):
			for x in range(16):
				for z in range(16):
					if y < 50 + np.sin(((self.x*16 + x) + 2 * (self.z * 16 + z)) / 10) * 5:
						self.blocks[x][y][z] = Blocks.Dirt

	def getMesh(self, nx, px, nz, pz): # parameters: neighporing chunks (negative x, positive x, negative z, positive z)
		vertices = []
		indices = []
		numVerts = 0
		for x in range(16):
			for z in range(16):
				for y in range(256):
					# top face:
					if self.blocks[x][y][z] != Blocks.Air and (y >= 255 or self.blocks[x][y+1][z]==Blocks.Air):
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
					if self.blocks[x][y][z] != Blocks.Air and (z >= 15 or self.blocks[x][y][z+1]==Blocks.Air):
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
					if self.blocks[x][y][z] != Blocks.Air and (x >= 15 or self.blocks[x+1][y][z]==Blocks.Air):
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