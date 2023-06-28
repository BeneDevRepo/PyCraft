#version 460

//in vec3 fragPos;
in FS_IN {
	vec2 uv;
};

out vec4 fragColor;

void main() {
    // vec2 uv = gl_FragCoord.xy / 800.;

    fragColor = vec4(uv, 0., 1.);
}