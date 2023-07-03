from  OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from  OpenGL.arrays.numbers import NumberHandler as NH # used to pass number references to pyopengl

# import pygame as pg
import glfw
import numpy as np

import time

from matrixMath import * # diy matrix math
from Chunk import Chunk
from World import World


d = .5
# vertices = [-d,  d, 1.,   0., 1., # top right triangle
#              d,  d, 1.,   1., 1.,
#              d, -d, 1.,   1., 0.,
             
#             -d,  d, 1.,   0., 1., # bottom left triangle
#              d, -d, 1.,   1., 0.,
#             -d, -d, 1.,   0., 0.]
vertices = [-d,  d, 1.,   0., 1., # top right triangle
             d,  d, 1.,   1., 1.,
             d, -d, 1.,   1., 0.,
            -d, -d, 1.,   0., 0.]
indices = [0, 1, 2,  0, 2, 3]
# vertices = (GLfloat * len(vertices))(*vertices)
vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.int32)

FLOATS_PER_POSITION = 3
FLOATS_PER_UV = 2
FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_UV


def main():
	# pg.init()
	if not glfw.init():
		print("Failed to initialize glfw")
		return

	# set OpenGL profile to 4.6 core:
	# pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
	# pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 6)
	# pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
	glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

	# setup window:
	# pg.display.set_mode((512, 512), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE, vsync = 1)
	window = glfw.create_window(512, 512, "GLFW Window", None, None)

	if not window:
		print("Failed to create glfw window")
		glfw.terminate()
		return

	glfw.make_context_current(window)

	# print("Version:", glGetString(GL_VERSION));

	# enable mouse capturing:
	# pg.mouse.set_visible(False)
	# pg.event.set_grab(True)
	glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED);

	glClearColor(0.5, 0.5, 0.5, 1.0)
	glEnable(GL_DEPTH_TEST)

	# enable backface culling:
	glEnable(GL_CULL_FACE)
	glCullFace(GL_FRONT) # visible face is defined in clockwise vertex order

	with open("main.vs.glsl") as file:
		vertex_shader_code = file.readlines();
	with open("main.fs.glsl") as file:
		fragment_shader_code = file.readlines();

	prog = shaders.compileProgram(
		shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER),
		shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
	)

	# mvp = glGetUniformLocation(prog, "MVP")
	u_model = glGetUniformLocation(prog, "model")
	u_view = glGetUniformLocation(prog, "view")
	u_projection = glGetUniformLocation(prog, "projection")



	# vertices, indices = Chunk(0, 0).getMesh()
	vertices, indices = Chunk(0, 0).getMesh(None, None, None, None)
	vertices, indices = np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)

	####  create object  ####
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

	# upload vertex buffer:
	# glNamedBufferStorage(vbo, len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)
	# glNamedBufferStorage(ebo, len(indices) * 4, indices, GL_DYNAMIC_STORAGE_BIT)

	# glBindVertexArray(vao)
	# glBufferStorage(GL_ARRAY_BUFFER, len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)
	# glBufferStorage(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, indices, GL_DYNAMIC_STORAGE_BIT)

	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, vertices, GL_DYNAMIC_DRAW)
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
	glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, indices, GL_DYNAMIC_DRAW)

	# configure vertex attributes:


	glEnableVertexArrayAttrib(vao,  0)
	glVertexArrayAttribFormat(vao,  0, FLOATS_PER_POSITION, GL_FLOAT, False, 0) # vao, attribIndex, size, type, normalized, offset
	glVertexArrayAttribBinding(vao, 0, 0)

	glVertexArrayAttribFormat(vao, 1, FLOATS_PER_UV, GL_FLOAT, False, FLOATS_PER_POSITION * 4) # vao, attribIndex, size, type, normalized, offset
	glVertexArrayAttribBinding(vao, 1, 0) # vao, attribIndex, bindingIndex
	glEnableVertexArrayAttrib(vao, 1) # vao, attribIndex
	####  /create object/  ####

	glUseProgram(prog)
	glBindVertexArray(vao)


	# chunks = {}
	# for x in range(-2, 2):
	# 	for z in range(-2, 2):
	# 		chunks[(x, 0, z)] = Chunk(x, z)
	world = World()
	

	aspectRatio = 1

	absTime = 0. # total elapsed time

	prev_time = time.perf_counter()

	accum = 0 # used for printing fps every second


	pos = np.array([0, 0, 0], dtype=np.float32)
	angles = [3.1415, 0] # horizontal (around y axis), vertical (around x axis)


	# while True:
	# 	for event in pg.event.get():
	# 		if event.type == pg.QUIT:
	# 			return
	# 		elif event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
	# 			return
	# 		elif event.type in [pg.VIDEORESIZE, pg.VIDEOEXPOSE]:
	# 			print("resize")
	# 			viewport = glGetIntegerv(GL_VIEWPORT) # [x0, y0, x1, y1]
	# 			aspectRatio = viewport[2] / viewport[3]
	# 			# glUniform1f(uniformAsp, viewport[2] / viewport[3]);
	# 	keys = pg.key.get_pressed()

	pmouseX, pmouseY = 0, 0
	mouseX, mouseY = 0, 0

	while not glfw.window_should_close(window):
		glfw.poll_events()

		if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
			return
		
		pmouseX, pmouseY = mouseX, mouseY
		mouseX, mouseY = glfw.get_cursor_pos(window)

		current_time = time.perf_counter()
		dt = current_time - prev_time
		prev_time = current_time

		accum += dt
		absTime += dt;

		if accum >= .5:
			accum -= .5
			print("FPS:", 1. / dt)

		# start drawing frame:
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# dx, dy = pg.mouse.get_rel()
		dx, dy = mouseX-pmouseX, mouseY-pmouseY
		angles[0] -= dx * 3.1415926535 / 180 * .1
		angles[1] -= dy * 3.1415926535 / 180 * .1
		angles[1] = max(-3.1415/2, min(3.1415/2, angles[1])) # constrain vertical viewing angle: -90deg < angle < 90deg
		# x += mouseX * .1
		# y += mouseY * .1


		# # vertical viewing angle:
		# viewDir = (0, np.sin(angles[1]), -np.cos(angles[1]))
		# # rotate around y axis by horizontal viewing angle:
		# viewDir = (
		# 	viewDir[0] * np.cos(angles[0]) - viewDir[2] * np.sin(angles[0]),
		# 	viewDir[1],
		# 	viewDir[0] * np.sin(angles[0]) + viewDir[2] * np.cos(angles[0])
		# )

		# # vertical viewing angle:
		# viewDir = (np.sin(angles[0]), 0, np.cos(angles[0]))
		# # rotate around y axis by horizontal viewing angle:
		# viewDir = (
		# 	viewDir[0],
		# 	viewDir[1] * np.cos(angles[1]) - viewDir[2] * np.sin(angles[1]),
		# 	viewDir[1] * np.sin(angles[1]) + viewDir[2] * np.cos(angles[1])
		# )

		# view = viewMat(pos, viewDir, (0, 1, 0))
		


		speed = 10.
		# moveDir = np.array([
		# 	keys[pg.K_d]     - keys[pg.K_a],
		# 	keys[pg.K_SPACE] - keys[pg.K_LSHIFT],
		# 	keys[pg.K_s]     - keys[pg.K_w]
		# ], dtype=np.float32)
		pressed = lambda key: glfw.get_key(window, key) == glfw.PRESS
		moveDir = np.array([
			pressed(glfw.KEY_D) - pressed(glfw.KEY_A),
			pressed(glfw.KEY_SPACE) - pressed(glfw.KEY_LEFT_SHIFT),
			pressed(glfw.KEY_S) - pressed(glfw.KEY_W)
		], dtype=np.float32)

		up = np.array([0, 1, 0], dtype=np.float32)
		front = np.array([np.cos(-angles[0]), 0, np.sin(-angles[0])], dtype=np.float32)
		right = np.cross(front, up)

		pos += moveDir[0] * front * speed * dt
		pos += moveDir[1] * up * speed * dt
		pos += moveDir[2] * right * speed * dt


		world.loadChunks(pos, 2)



		# moveDir = moveDir @ view[:3][:3]
		# pos += front * (moveDir[2] * speed)

		# pos[0] += moveDir[0] * speed
		# pos[1] += moveDir[1] * speed
		# pos[2] -= moveDir[2] * speed
		# print(mouseX, mouseY)





		# setup MVP matrix:
		# proj = perspectiveProj(90, 1., .01, 100.)
		proj = perspectiveProj(90. * 3.1415926535 / 180., aspectRatio, .01, 1000.)
		# proj = np.identity(4, dtype=np.float32)

		# view = np.identity(4, dtype=np.float32)
		# view = viewMat(pos, (0, 0, -1), (0, 1, 0))
		
		# view = viewMat(pos, viewDir, (0, 1, 0))
		# view = translate((x, 0, y))

		# https://www.mauriciopoppe.com/notes/computer-graphics/viewing/camera/first-person-shot/
		sa = np.sin(angles[0])
		ca = np.cos(angles[0])
		sb = np.sin(angles[1])
		cb = np.cos(angles[1])
		view = np.array([
			[ ca, sa*sb, sa*cb, 0],
			[  0,    cb,   -sb, 0],
			[-sa, ca*sb, ca*cb, 0],
			[  0,     0,     0, 1]
		], dtype=np.float32)
		view = translate(-pos) @ view

		model = np.identity(4, dtype=np.float32)
		# model = translate((np.cos(absTime), np.sin(absTime), 0))
		# model = translate((x*.1, -y*.1, 0))
		# model = translate(pos)


		# glUniformMatrix4fv(mvp, 1, GL_FALSE, mvpMatrix)
		glUniformMatrix4fv(u_model, 1, GL_FALSE, model)
		glUniformMatrix4fv(u_view, 1, GL_FALSE, view)
		glUniformMatrix4fv(u_projection, 1, GL_FALSE, proj)

		# glDrawArrays(GL_TRIANGLES, 0, 6) # draw
		glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None) # draw

		# pg.display.flip()
		glfw.swap_buffers(window)
	
	glfw.terminate()


if __name__ == '__main__':
	try:
		main()
	except Exception as error:
		# pg.quit()
		glfw.terminate()
		print("Failed!", error)
		time.sleep(1000)