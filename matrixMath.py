import numpy as np

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
    # return np.array([[1,0,0,x],
    #                   [0,1,0,y],
    #                   [0,0,1,z],
    #                   [0,0,0,1]], dtype=np.float32)
    return np.array([[1,0,0,0],
                      [0,1,0,0],
                      [0,0,1,0],
                      [x,y,z,1]], dtype=np.float32)

def normalize(v):
	l = np.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
	return np.array([v[0] / l, v[1] / l, v[2] / l], dtype=np.float32)

def viewMat(eye, dir, up):
	front = normalize(dir)
	up = normalize(up)
	right = np.cross(front, up)
	up = np.cross(right, front)
	M = np.matrix(np.identity(4))
	# M = np.identity(4)
	M[:3,:3] = np.vstack([right, up, front])
	# M = np.array([
	# 	 [*right, 0],
	# 	 [*up, 0],
	# 	 [*-front, 0],
	# 	#  [right[0], up[0], -front[0], 0],
	# 	#  [right[1], up[1], -front[1], 0],
	# 	#  [right[2], up[2], -front[2], 0],
	# 	 [0, 0, 0, 1],
	# 	],
	#     dtype=np.float32)

	M = np.array(M, dtype=np.float32)

	# # M[3, :3] = eye
	# M[3, 0] = -eye[0]
	# M[3, 1] = -eye[1]
	# M[3, 2] = -eye[2]
	# return M
	T = translate(-eye)
	# return M @ T
	# return np.array(M * T, dtype=np.float32)
	# return np.array(M @ T, dtype=np.float32)
	# return T * M
	return T @ M
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