#version 330 core
in vec2 vTexCoord;
layout(location=0) out vec4 oColor;
layout(location=1) out vec4 oBright;
layout(location=2) out vec4 oID;

uniform float uRadius;
uniform float uTime;
uniform float uAlpha;
uniform vec3 uCoreCol;
uniform vec3 uEdgeCol;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453);
}
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
               mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}

void main() {
    vec2 uv = vTexCoord * 2.0 - 1.0;
    float r = length(uv);
    
    // Shell effect
    float shell = smoothstep(0.8, 1.0, r) * smoothstep(1.2, 1.0, r);
    float core = smoothstep(0.8, 0.0, r);
    
    // Ripple rings
    float rings = sin(r * 20.0 - uTime * 8.0) * 0.5 + 0.5;
    rings *= shell;
    
    vec3 col = mix(uCoreCol, uEdgeCol, r) * (core + shell * 2.0 + rings);
    float a = (core * 0.6 + shell + rings * 0.3) * uAlpha;
    
    oColor = vec4(col, a);
    oBright = vec4(col * max(0.0, a - 0.3) * 2.0, 1.0);
    oID = vec4(0);
}
