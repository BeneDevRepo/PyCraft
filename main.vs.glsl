#version 460


in vec3 i_position;
in vec3 i_normal;
in vec2 i_uv;

// out vec3 fragPos;

out FS_IN {
	vec3 fragPos;
	vec3 normal;
	vec2 uv;
};

// uniform mat4 MVP;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
	// vec4 transformed = MVP * vec4(i_position.xyz, 1.);
	// vec4 transformed = vec4(i_position.xyz, 1.) * MVP;
    // fragPos = transformed.xyz;

	fragPos = vec3(model * vec4(i_position, 1.));
	// vec3 normal = mat3(transpose(inverse(model))) * i_normal;

	normal = i_normal;
	uv = i_uv;
	// uv = transformed.xy;

    gl_Position = projection * view * vec4(fragPos, 1.);
    // gl_Position = vec4(transformed.xyz, 1.);
    // gl_Position = transformed;
}