#version 460

precision highp float;

in FS_IN {
	vec3 fragPos;
	vec3 normal;
	vec2 uv;
	flat uint block;
};


out vec4 fragColor;

uniform vec3 viewPos;

// quelle der nächsten 2 Funktionen (Nutzung vorerst nur zu Demonstrationszwecken): https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
float rand(in vec2 n) { 
	return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453);
}

float noise(in vec2 p){
	vec2 ip = floor(p);
	vec2 u = fract(p);
	u = u*u*(3.0-2.0*u);

	float res = mix(
		mix(rand(ip),rand(ip+vec2(1.0,0.0)),u.x),
		mix(rand(ip+vec2(0.0,1.0)),rand(ip+vec2(1.0,1.0)),u.x),u.y);
	return res*res;
}

vec3 aces(in vec3 x) {
	const float a = 2.51;
	const float b = .03;
	const float c = 2.43;
	const float d = .59;
	const float e = .14;
	return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0., 1.);
}


#define BLOCK_STONE 1u
#define BLOCK_DIRT 2u
#define BLOCK_GRASS 3u
#define BLOCK_SNOW 4u

#define BLOCK_WATER 20u


void main() {
    // demo-Textur mittels noise:
	vec2 pixPos = floor(uv * 16.) + round(fragPos.xy);
	vec3 albedo = vec3(.7, 0., 1.);

	if(block == BLOCK_STONE) {
		albedo = vec3(mix(vec3(.3), vec3(.4), noise(pixPos))); // stone
	} else if(block == BLOCK_DIRT) {
		albedo = vec3(mix(vec3(.25, .12, .0), vec3(.35, .15, .0), noise(pixPos))); // dirt
	} else if(block == BLOCK_GRASS) {
		albedo = vec3(mix(vec3(.3, .5, .2), vec3(.1, .3, .1), noise(pixPos))); // grass
	} else if(block == BLOCK_SNOW) {
		albedo = vec3(mix(vec3(.85), vec3(1.), noise(pixPos))); // snow
	} else if(block == BLOCK_WATER) {
		albedo = vec3(mix(vec3(.3, .3, .6), vec3(.2, .4, .8), noise(pixPos))); // water
	}

	// Simple Demobeleuchtung ("Phong-Shading"):
	vec3 lightDir = normalize(vec3(-1, 2, .5));
	vec3 viewDir = normalize(viewPos - fragPos);

	vec3 ambient = vec3(.2);
	vec3 diffuse = max(0., dot(lightDir, normal)) * vec3(1., .6, .5);
	vec3 specular = pow(max(0., dot(reflect(-lightDir, normal), viewDir)), 128.) * vec3(1., .6, .5);

	vec3 lightCol = ambient + diffuse * .5 + specular * .5;

	vec3 col = albedo * lightCol;

	// tone-mapping:
	col = aces(col);

	// gamma correction:
	col = pow(col, vec3(1. / 2.2));

    fragColor = vec4(col, 1.);
}