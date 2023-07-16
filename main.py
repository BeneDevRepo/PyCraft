from  OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from  OpenGL.arrays.numbers import NumberHandler as NH # used to pass number references to pyopengl

import pygame as pg
import numpy as np

import time

from matrixMath import * # diy matrix math
from World import World


def main():
	pg.init()

	# set OpenGL profile to 4.6 core:
	pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
	pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 6)
	pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
	pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

	# setup window:
	pg.display.set_mode((512, 512), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE, vsync = 1)


	# print("Version:", glGetString(GL_VERSION));

	# enable mouse capturing:
	pg.mouse.set_visible(False)
	pg.event.set_grab(True)

	glClearColor(.8, .8, 1., 1.0)
	glEnable(GL_DEPTH_TEST)

	# enable backface culling:
	glEnable(GL_CULL_FACE)
	glCullFace(GL_FRONT) # visible face is defined in clockwise vertex order

	with open("main.vs.glsl") as file:
		vertex_shader_code = file.readlines();
	with open("main.fs.glsl") as file:
		fragment_shader_code = file.readlines();

	vertShader = shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER)
	fragShader = shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)

	prog = shaders.compileProgram(vertShader, fragShader, validate=False)


	u_model = glGetUniformLocation(prog, "model")
	u_view = glGetUniformLocation(prog, "view")
	u_projection = glGetUniformLocation(prog, "projection")

	u_viewPos = glGetUniformLocation(prog, "viewPos")


	glUseProgram(prog)

	world = World()

	aspectRatio = 1

	absTime = 0. # total elapsed time
	prev_time = time.perf_counter()
	accum = 0 # used for printing fps every second


	pos = np.array([0, 100, 0], dtype=np.float32)
	angles = [3.1415, 0] # horizontal (around y axis), vertical (around x axis)

	stop = False
	while not stop:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				stop = True
			elif event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
				stop = True
			elif event.type in [pg.VIDEORESIZE, pg.VIDEOEXPOSE]:
				print("resize")
				viewport = glGetIntegerv(GL_VIEWPORT) # [x0, y0, x1, y1]
				aspectRatio = viewport[2] / viewport[3]
				# glUniform1f(uniformAsp, viewport[2] / viewport[3]);
		keys = pg.key.get_pressed()


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

		dx, dy = pg.mouse.get_rel()
		angles[0] -= dx * 3.1415926535 / 180 * .1
		angles[1] -= dy * 3.1415926535 / 180 * .1
		angles[1] = max(-3.1415/2, min(3.1415/2, angles[1])) # constrain vertical viewing angle: -90deg < angle < 90deg


		speed = 10. + keys[pg.K_LCTRL] * 20.;
		moveDir = np.array([
			keys[pg.K_d]     - keys[pg.K_a],
			keys[pg.K_SPACE] - keys[pg.K_LSHIFT],
			keys[pg.K_s]     - keys[pg.K_w]
		], dtype=np.float32)

		up = np.array([0, 1, 0], dtype=np.float32)
		front = np.array([np.cos(-angles[0]), 0, np.sin(-angles[0])], dtype=np.float32)
		right = np.cross(front, up)

		pos += moveDir[0] * front * speed * dt
		pos += moveDir[1] * up * speed * dt
		pos += moveDir[2] * right * speed * dt


		world.loadChunks(pos, 5)
		# world.loadChunks((0, 0, 0), 2)






		# setup matrices:
		proj = perspectiveProj(90. * 3.1415926535 / 180., aspectRatio, .01, 1000.)
		glUniformMatrix4fv(u_projection, 1, GL_FALSE, proj)

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
		glUniformMatrix4fv(u_view, 1, GL_FALSE, view)
		
		glUniform3fv(u_viewPos, 1, pos)

		for chunkPos in world.chunks.keys():
			model = translate((chunkPos[0] * 16, 0, chunkPos[1] * 16))
			glUniformMatrix4fv(u_model, 1, GL_FALSE, model)

			mesh = world.meshes[chunkPos]
			vao, vbo, ebo, numIndices = mesh

			if numIndices == 0:
				continue

			glBindVertexArray(vao)
			glDrawElements(GL_TRIANGLES, numIndices, GL_UNSIGNED_INT, None) # draw

		pg.display.flip()


	## Shutdown:
	world.shutdown()



if __name__ == '__main__':
	try:
		main()
	except Exception as error:
		pg.quit()
		print("Failed!", error)
		time.sleep(1000)