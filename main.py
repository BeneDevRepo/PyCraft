from anyio import Event
from  OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from  OpenGL.arrays.numbers import NumberHandler as NH

import pygame as pg
import numpy as np

import time


# vertices = [-1.,  1., 0., 1., # top right triangle
#              1.,  1., 0., 1.,
#              1., -1., 0., 1.,
             
#             -1.,  1., 0., 1., # bottom left triangle
#              1., -1., 0., 1.,
#             -1., -1., 0., 1.]
d = .5
# vertices = [-d,  d, 1., 1., # top right triangle
#              d,  d, 1., 1.,
#              d, -d, 1., 1.,
             
#             -d,  d, 1., 1., # bottom left triangle
#              d, -d, 1., 1.,
#             -d, -d, 1., 1.]
# vertices = [-d,  d, -1., # top right triangle
#              d,  d, -1.,
#              d, -d, -1.,
             
#             -d,  d, -1., # bottom left triangle
#              d, -d, -1.,
#             -d, -d, -1.]
vertices = [-d,  d, -1.,   0., 1., # top right triangle
             d,  d, -1.,   1., 1.,
             d, -d, -1.,   1., 0.,
             
            -d,  d, -1.,   0., 1., # bottom left triangle
             d, -d, -1.,   1., 0.,
            -d, -d, -1.,   0., 0.]
vertices = (GLfloat * len(vertices))(*vertices)
# vertices = np.array(vertices, dtype=np.float32)
FLOATS_PER_POSITION = 3
FLOATS_PER_UV = 2
FLOATS_PER_VERTEX = FLOATS_PER_POSITION + FLOATS_PER_UV


def perspectiveProj(fov, aspect_ratio, near_plane, far_plane):
	num = 1.0 / np.tan(fov / 2.0)
	num9 = num / aspect_ratio
	return np.array([
		[num9, 0.0, 0.0, 0.0],
		[0.0, num, 0.0, 0.0],
		[0.0, 0.0, far_plane / (near_plane - far_plane), -1.0],
		[0.0, 0.0, (near_plane * far_plane) / (near_plane - far_plane), 0.0]
	], dtype=np.float32)
	# return np.array([
	# 	num9, 0.0, 0.0, 0.0,
	# 	0.0, num, 0.0, 0.0,
	# 	0.0, 0.0, far_plane / (near_plane - far_plane), -1.0,
	# 	0.0, 0.0, (near_plane * far_plane) / (near_plane - far_plane), 0.0
	# ], dtype=np.float32)

# def perspectiveProj(fovVert, aspect, near, far):
#     s = 1. / np.tan(np.radians(fovVert) / 2.)
#     sx, sy = s / aspect, s
#     zz = (far + near) / (near - far)
#     zw = 2 * far * near / (near - far)
#     return np.matrix([[sx, 0,  0,  0],
#                       [0,  sy, 0,  0],
#                       [0,  0, zz, zw],
#                       [0,  0, -1, 0]])

def translate(xyz):
    x, y, z = xyz
    return np.matrix([[1,0,0,x],
                      [0,1,0,y],
                      [0,0,1,z],
                      [0,0,0,1]], dtype=np.float32)

def viewMat(eye, dir, up):
    F = dir
    f = normalize(F)
    U = normalize(up[:3])
    s = np.cross(f, U)
    u = np.cross(s, f)
    M = np.matrix(np.identity(4))
    M[:3,:3] = np.vstack([s,u,-f])
    T = translate(-eye)
    return M * T
# def lookat(eye, target, up):
#     F = target[:3] - eye[:3]
#     f = normalize(F)
#     U = normalize(up[:3])
#     s = np.cross(f, U)
#     u = np.cross(s, f)
#     M = np.matrix(np.identity(4))
#     M[:3,:3] = np.vstack([s,u,-f])
#     T = translate(-eye)
#     return M * T


def main():
	pg.init()

	# set OpenGL profile to 4.6 core:
	pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
	pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 6)
	pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

	pg.display.set_mode((512, 512), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE, vsync = 1)

	glClearColor(0.5, 0.5, 0.5, 1.0)
	glEnable(GL_DEPTH_TEST)
	glDisable(GL_CULL_FACE)

	with open("main.vs.glsl") as file:
		vertex_shader_code = file.readlines();
	with open("main.fs.glsl") as file:
		fragment_shader_code = file.readlines();

	prog = shaders.compileProgram(
		shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER),
		shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
	)

	mvp = glGetUniformLocation(prog, "MVP")
	# iTime = glGetUniformLocation(prog, "iTime")
	# uniformAsp = glGetUniformLocation(prog, "aspectRatio")



	####  create object  ####
	# Create a new VAO (Vertex Array Object):
	vao = GLuint(-1)
	glCreateVertexArrays(1, NH().dataPointer(vao))

	# Generate buffers to hold our vertices:
	vbo = GLuint(-1)
	glCreateBuffers(1, NH().dataPointer(vbo))

	glNamedBufferStorage(vbo, len(vertices) * 4, vertices, GL_DYNAMIC_STORAGE_BIT)

	glVertexArrayVertexBuffer(vao, 0, vbo, 0, FLOATS_PER_VERTEX * 4) # vao, bindIndex, buffer, offset, stride

	glEnableVertexArrayAttrib(vao,  0)
	glVertexArrayAttribFormat(vao,  0, FLOATS_PER_POSITION, GL_FLOAT, False, 0) # vao, attribIndex, size, type, normalized, offset
	glVertexArrayAttribBinding(vao, 0, 0)

	glVertexArrayAttribFormat(vao, 1, FLOATS_PER_UV, GL_FLOAT, False, FLOATS_PER_POSITION * 4) # vao, attribIndex, size, type, normalized, offset
	glVertexArrayAttribBinding(vao, 1, 0) # vao, attribIndex, bindingIndex
	glEnableVertexArrayAttrib(vao, 1) # vao, attribIndex
	####  /create object/  ####



	glUseProgram(prog)
	glBindVertexArray(vao)

	# proj = perspectiveProj(90, 1., .01, 100.)
	proj = perspectiveProj(90. * 3.1415926535 / 180., 1., .01, 100.)
	view = np.identity(4, dtype=np.float32)
	# view = np.matmul(translate((10, 0, 1)), view)
	view = np.matmul(view, translate((1, 0, 1)))
	# view = translate((100, 0, 0))
	model = np.identity(4, dtype=np.float32)

	# mvpMatrix = np.matmul(proj, view)
	mvpMatrix = np.matmul(view, proj)
	# mvpMatrix = np.matmul(np.matmul(proj, view), model)
	# mvpMatrix = proj

	glUniformMatrix4fv(mvp, 1, GL_FALSE, mvpMatrix)


	absTime = 0. # total elapsed time

	prev_time = time.perf_counter()

	accum = 0 # used for printing fps every second

	while True:
		current_time = time.perf_counter()
		dt = current_time - prev_time
		prev_time = current_time

		accum += dt
		absTime += dt;
		
		# glUniform1f(iTime, absTime)

		
		if accum >= .5:
			accum -= .5
			print("FPS:", 1. / dt)
		
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return
			elif event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
				return
			elif event.type in [pg.VIDEORESIZE, pg.VIDEOEXPOSE]:
				print("resize")
				# viewport = glGetIntegerv(GL_VIEWPORT) # [x0, y0, x1, y1]
				# glUniform1f(uniformAsp, viewport[2] / viewport[3]);

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glDrawArrays(GL_TRIANGLES, 0, 6)

		pg.display.flip()


if __name__ == '__main__':
	try:
		main()
	except Exception as error:
		pg.quit()
		print("Failed!", error)
		time.sleep(1000)