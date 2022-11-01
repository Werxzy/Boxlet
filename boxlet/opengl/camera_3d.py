import numpy as np
import math

from boxlet import Shader, Tmath, manager, Transform, FrameBufferStep


class Camera3D(Transform, FrameBufferStep):
	def __init__(self, width=0, height=0, width_mult=1, height_mult=1, depth=True, nearest=False, queue=0, pass_names: list[str] = None) -> None:
		super().__init__(width, height, width_mult, height_mult, depth, nearest, queue, pass_names)

		self.perspective(90, 16.0/9.0, 0.1, 1000)
		# self.orthographic(-5, 5, -5 * 9 / 16, 5 * 9 / 16, 0.1, 1000)
		Shader.add_global_matrix_uniform('box_viewProj', np.identity(4, dtype=np.float32))

	def prepare(self):
		super().prepare()
		Shader.set_global_uniform('box_viewProj', np.matmul(np.linalg.inv(self.model_matrix), self.proj_matrix))

	def perspective(self, fov:float, aspect:float, near:float, far:float):
		f = math.tan(math.radians(fov)/2)

		self.clip_near, self.clip_far = near, far

		x = 1 / f
		y = aspect * x
		z1 = (near + far) / (near - far)
		z2 = 2 * near * far / (near - far)

		self.proj_matrix = np.array([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, -z1, 1], [0, 0, z2, 0]])
		self.inv_proj_matrix = np.linalg.inv(self.proj_matrix)
		self.proj_type_perspective = True


	def orthographic(self, left:float, right:float, bottom:float, top:float, near:float, far:float):
		self.clip_near, self.clip_far = near, far

		dx = 1 / (right - left)
		dy = 1 / (top - bottom)
		dz = 1 / (far - near)

		rx = -(right + left) * dx
		ry = -(top + bottom) * dy
		rz = -(far + near) * dz

		self.proj_matrix = np.array([[2*dx, 0, 0, rx], [0, 2*dy, 0, ry], [0, 0, 2*dz, rz], [0, 0, 0, 1]]).T
		self.inv_proj_matrix = np.linalg.inv(self.proj_matrix)
		self.proj_type_perspective = False

	# def orthographic_simple(self, width:float, height:float, depth:float):
	# 	# 0,0 is the center of the screen

	# 	dx = 4 / width
	# 	dy = 4 / height
	# 	dz = -2 / depth
		
		# self.proj_matrix = return np.array([[dx, 0, 0, 0], [0, dy, 0, 0], [0, 0, dz, -1], [0, 0, 0, 1]])
		# self.inv_proj_matrix = np.linalg.inv(self.proj_matrix)


	def get_mouse_ray(self, pos):
		'Returns the ray of the given mouse coordinate from screen space to world space.\n\nreturns (pos, direction)'

		coord = pos / manager.display_size * 2 - 1

		if self.proj_type_perspective:
			ray_eye = np.matmul(self.inv_proj_matrix, np.array([coord[0],-coord[1],-1,1]))		
			ray_world = np.matmul(np.linalg.inv(self.model_matrix), np.array([ray_eye[0],ray_eye[1],1,0]))

			return self.position, Tmath.normalize(ray_world[0:3])

		else: # orthographic projection
			start_eye = np.matmul(self.inv_proj_matrix.T, np.array([coord[0],-coord[1],-1,1]))		
			start_world = np.matmul(self.model_matrix.T, np.array([start_eye[0],start_eye[1],start_eye[2],1]))

			return start_world[:3], Tmath.normalize(self.forward)

