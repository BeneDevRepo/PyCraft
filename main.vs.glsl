#version 460


layout (location = 0) in vec3 i_position;
layout (location = 1) in vec3 i_normal;
layout (location = 2) in vec2 i_uv;
layout (location = 3) in uint extra;

out FS_IN {
	vec3 fragPos;
	vec3 normal;
	vec2 uv;
	flat uint block;
};

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
	fragPos = vec3(model * vec4(i_position, 1.));
	normal = mat3(transpose(inverse(model))) * i_normal;

	uv = i_uv;
	block = extra & 0xFFu;

    gl_Position = projection * view * vec4(fragPos, 1.);
}