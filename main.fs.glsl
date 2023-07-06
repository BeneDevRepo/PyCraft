#version 460

//in vec3 fragPos;
in FS_IN {
	vec3 fragPos;
	vec3 normal;
	vec2 uv;
};

out vec4 fragColor;

uniform vec3 viewPos;

void main() {
    // vec2 uv = gl_FragCoord.xy / 800.;

	vec3 albedo = vec3(uv, 0.);

	vec3 lightDir = normalize(vec3(-1, 2, .5));
	vec3 viewDir = normalize(viewPos - fragPos);

	vec3 ambient = vec3(.2);
	vec3 diffuse = max(0., dot(lightDir, normal)) * vec3(1., .5, .2);
	vec3 specular = max(0., dot(reflect(-lightDir, normal), viewDir)) * vec3(1., .5, .2);
	vec3 col = ambient + diffuse + specular;

    fragColor = vec4(col, 1.);

    // fragColor = vec4(fragPos, 1.);
    // fragColor = vec4(normal, 1.);
    // fragColor = vec4(uv, 0., 1.);
}