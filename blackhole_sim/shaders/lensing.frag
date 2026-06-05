#version 330 core
layout (location = 0) out vec4 oColor;

in vec2 vTexCoord;
uniform sampler2D uScene;
uniform vec2 uBHScreen;   // black hole NDC position
uniform float uRsScreen;   // Rs in screen pixels (normalized 0-1)
uniform float uStrength;

void main() {
    vec2 texCoord = vTexCoord;
    vec2 toCenter = uBHScreen - texCoord;
    float dist = length(toCenter);
    
    // Gravitational deflection: theta ≈ 4GM/c^2 r
    float theta = uRsScreen / (dist + 0.001);
    vec2 deflect = normalize(toCenter) * theta * 0.1 * uStrength;
    
    vec3 lensed = texture(uScene, texCoord + deflect).rgb;
    
    // Einstein ring brightening
    float ring = smoothstep(uRsScreen * 0.9, uRsScreen, dist) - smoothstep(uRsScreen, uRsScreen * 1.1, dist);
    lensed += vec3(1.0, 0.8, 0.4) * ring * 2.0 * uStrength;
    
    oColor = vec4(lensed, 1.0);
}
