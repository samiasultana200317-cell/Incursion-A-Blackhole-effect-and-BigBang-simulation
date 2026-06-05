#version 330 core
in vec2 vTexCoord;
layout(location=0) out vec4 oColor;
layout(location=1) out vec4 oBright;
layout(location=2) out vec4 oID;

uniform float uTime;
uniform float uAmplitude;
uniform float uSpeed;
uniform vec3 uColA; // hot white
uniform vec3 uColB; // orange
uniform vec3 uColC; // red
uniform float uAlpha;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f*f*(3.0 - 2.0*f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x),
               mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}

float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    for(int i = 0; i < 5; i++) {
        v += a * noise(p); p *= 2.0; a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = vTexCoord;
    uv += vec2(sin(uv.y*4.0+uTime*uSpeed), cos(uv.x*4.0+uTime*uSpeed)) * 0.015;
    
    float n = fbm(uv * 3.0 + vec2(uTime*0.4*uSpeed, uTime*0.2*uSpeed))
            + fbm(uv * 6.0 - vec2(uTime*0.3*uSpeed, uTime*0.5*uSpeed)) * 0.5;
    n *= uAmplitude;
    n = clamp(n, 0.0, 1.0);
    
    vec3 col;
    if(n < 0.3) col = mix(uColC, uColB, n / 0.3);
    else if(n < 0.7) col = mix(uColB, uColA, (n-0.3)/0.4);
    else col = uColA;
    
    oColor = vec4(col * uAlpha, uAlpha);
    oBright = vec4(col * max(0.0, n - 0.6) * 3.0, 1.0);
    oID = vec4(0);
}
