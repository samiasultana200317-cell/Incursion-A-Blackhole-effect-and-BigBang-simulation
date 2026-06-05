#version 330 core
layout (location = 0) out vec4 oColor;

in vec2 vTexCoord;
uniform sampler2D uScene;
uniform sampler2D uBloom;
uniform float uExposure;
uniform float uBloomStr;
uniform float uFlash;

void main() {
    const float gamma = 2.2;
    vec3 sceneColor = texture(uScene, vTexCoord).rgb;
    vec3 bloomColor = texture(uBloom, vTexCoord).rgb;
    
    vec3 hdrColor = sceneColor + bloomColor * uBloomStr;
    
    // Exposure tone mapping
    vec3 result = vec3(1.0) - exp(-hdrColor * uExposure);
    // Gamma correction
    result = pow(result, vec3(1.0 / gamma));
    
    // Add flash
    result = mix(result, vec3(1.0), uFlash);
    
    oColor = vec4(result, 1.0);
}
