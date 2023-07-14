#pragma once

#include <cstdint>
#include <cmath>

#include "SimplexNoise.hpp"
#include "constants.hpp"


inline float mapContinental(const float t) {
	static const auto lerp =
		[](const float a, const float b, const float t)
			-> float { return (1. - t) * a + t * b; };
	static const auto scaleT =
		[](const float start, const float end, const float t)
			-> float { return (t - start) / (end - start); };
	static const auto calc =
		[&](const float x1, const float x2, const float y1, const float y2, const float t)
			-> float { return lerp(y1, y2, scaleT(x1, x2, t)); };


	if(t < .38)
		return calc(.0, .38, .0, .05, t);

	if(t < .4)
		return calc(.38, .4, .05, .3, t);

	if(t < .6)
		return calc(.4, .6, .3, .32, t);

	if(t < .7)
		return calc(.6, .7, .32, .7, t);
	
	return calc(.7, 1., .7, .75, t);
}

inline float octaveNoise(const float x, const float y, const float z, const size_t octaves) {
	static const SimplexNoise sNoise;

	float res = 0;
	
	for(size_t i = 0; i < octaves; i++) {
		res += .5 * sNoise.noise(x * (1 << i), y * (1 << i), z * (1 << i)) / (1 << i);
	}

	return res * .5 + .5;
}

inline float octaveNoise(const float x, const float y, const size_t octaves) {
	static const SimplexNoise sNoise;

	float res = 0;
	
	for(size_t i = 0; i < octaves; i++) {
		res += .5 * sNoise.noise(x * (1 << i), y * (1 << i)) / (1 << i);
	}

	return res * .5 + .5;
}

inline Block getBlock(const int64_t x, const int64_t y, const int64_t z) {
	static const auto lerp =
		[](const float a, const float b, const float t)
			-> float { return (1. - t) * a + t * b; };

	static const auto smoothstep =
		[&](float x, const float e0, const float e1)
			-> float {
				if(x <= 0) return 0;
				if(x >= 1) return 1;
				x = (x - e0) / (e1 - e0);
				x = (x<0) ? 0 : ((x>1) ? 1 : x);
				return 3*x*x - 2*x*x*x;
			};


	const float continentality = octaveNoise(x * .0005, z * .0005, 8);
	const float height = mapContinental(continentality) * 255;

	const float cliffScale = .0002;
	const float cliffNoise = octaveNoise(x * cliffScale, z * cliffScale, 8);
	const float cliffFactor = smoothstep(cliffNoise, .51, .51 + .01)
									* smoothstep(cliffNoise, .53, .53 - .01);

	const bool base = y < height * (1 - cliffFactor * .8);

	if(base) {
		if(y < 100) {
			return BLOCK_GRASS;
		} else if(y < 170) {
			return BLOCK_STONE;
		}

		return BLOCK_SNOW;
	}

	return y < 64 ? BLOCK_WATER : BLOCK_AIR;
}