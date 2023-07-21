import numpy as np

from  OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from  OpenGL.arrays.numbers import NumberHandler as NH # used to pass number references to pyopengl


FLOATS_PER_POSITION = 2
FLOATS_PER_UV = 2
FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_UV


class Gui:
	def __init__(self):
		vertShader = shaders.compileShader("""
		#version 460

		layout (location = 0) in vec2 i_pos;
		layout (location = 1) in vec2 i_uv;

		out vec2 uv;

		void main() {
			uv = i_uv;
			gl_Position = vec4(i_pos, 0., 1.);
		}
		""", GL_VERTEX_SHADER)
		fragShader = shaders.compileShader("""
		#version 460

		in vec2 uv;
		out vec4 fragColor;

		void main() {
			// fragColor = vec4(uv, 0., 1.);
			fragColor = vec4(vec3(1.), 1.);
		}
		""", GL_FRAGMENT_SHADER)

		self.prog = shaders.compileProgram(vertShader, fragShader, validate=False)
		
		
        # Create Vertex Array Object:
		self.vao = GLuint(-1)
		glCreateVertexArrays(1, NH().dataPointer(self.vao))

		# Create vertex buffer:
		self.vbo = GLuint(-1)
		glCreateBuffers(1, NH().dataPointer(self.vbo))

		# Create vertex buffer:
		self.ebo = GLuint(-1)
		glCreateBuffers(1, NH().dataPointer(self.ebo))

		# link vao, vbo and ebo
		glVertexArrayVertexBuffer(self.vao, 0, self.vbo, 0, FLOATS_PER_VERTEX * 4) # vao, bindIndex, buffer, offset, stride
		glVertexArrayElementBuffer(self.vao, self.ebo) # vao, buffer

		# configure vertex attributes:
		glEnableVertexArrayAttrib(self.vao,  0)
		glVertexArrayAttribFormat(self.vao,  0, FLOATS_PER_POSITION, GL_FLOAT, False, (0) * 4) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(self.vao, 0, 0)

		glVertexArrayAttribFormat(self.vao, 1, FLOATS_PER_UV, GL_FLOAT, False, (FLOATS_PER_POSITION) * 4) # vao, attribIndex, size, type, normalized, offset
		glVertexArrayAttribBinding(self.vao, 1, 0) # vao, attribIndex, bindingIndex
		glEnableVertexArrayAttrib(self.vao, 1) # vao, attribIndex


		viewport = glGetIntegerv(GL_VIEWPORT) # [x0, y0, x1, y1]
		px = 1. / viewport[2]
		py = 1. / viewport[3]

		self.vertices = np.array([
			-px * 16,  py * 3, 0., 0., # horizontal
			 px * 16,  py * 3, 1., 0.,
			-px * 16, -py * 3, 0., 1.,
			 px * 16, -py * 3, 1., 1.,

			-px * 3,  py * 16, 0., 0., # vertical
			 px * 3,  py * 16, 1., 0.,
			-px * 3, -py * 16, 0., 1.,
			 px * 3, -py * 16, 1., 1.,
		], dtype=np.float32)

		self.indices = np.array([
			0, 1, 3,  0, 3, 2, # horizontal
			4, 5, 7,  4, 7, 6, # vertical
		], dtype=np.uint32)

		glNamedBufferStorage(self.vbo, len(self.vertices) * 4, self.vertices, GL_DYNAMIC_STORAGE_BIT)
		glNamedBufferStorage(self.ebo, len(self.indices) * 4, self.indices, GL_DYNAMIC_STORAGE_BIT)



	def draw(self):
		viewport = glGetIntegerv(GL_VIEWPORT) # [x0, y0, x1, y1]
		px = 1. / viewport[2]
		py = 1. / viewport[3]

		# self.vertices = np.array([
		# 	-px * 6,  py * 2, 0., 0.,
		# 	 px * 6,  py * 2, 1., 0.,
		# 	-px * 6, -py * 2, 0., 1.,
		# 	 px * 6, -py * 2, 1., 1.,
		# ], dtype=np.float32)

		# self.indices = np.array([
		# 	0, 1, 3,  0, 3, 2,
		# ], dtype=np.uint32)

		# glNamedBufferStorage(self.vbo, len(self.vertices) * 4, self.vertices, GL_DYNAMIC_STORAGE_BIT)
		# glNamedBufferStorage(self.ebo, len(self.indices) * 4, self.indices, GL_DYNAMIC_STORAGE_BIT)

		
		glUseProgram(self.prog)

		glBindVertexArray(self.vao)

		glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)