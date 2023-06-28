#version 460


in vec3 i_position;
in vec2 i_uv;

// out vec3 fragPos;

out FS_IN {
	vec2 uv;
};

uniform mat4 MVP;

void main() {
	vec4 transformed = MVP * vec4(i_position.xyz, 1.);
    // fragPos = transformed.xyz;

	uv = i_uv;
	// uv = transformed.xy;

    // gl_Position = vec4(transformed.xyz, 1.);
    gl_Position = transformed;
}