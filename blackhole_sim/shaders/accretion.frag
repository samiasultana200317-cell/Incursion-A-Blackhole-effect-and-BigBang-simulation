#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in float vTemp;
in float vRadii;

void main() {
    float t = vTemp / 40000.0;
    vec3 col = mix(vec3(1.0, 0.3, 0.0), mix(vec3(1.0, 0.9, 0.6), vec3(0.6, 0.8, 1.0), clamp(t*2.0 - 1.0, 0.0, 1.0)), clamp(t, 0.0, 1.0));
    
    vec2 c = gl_PointCoord - 0.5;
    float dist = length(c);
    float alpha = smoothstep(0.5, 0.2, dist);
    if (alpha < 0.01) discard;
    
    oColor = vec4(col, alpha);
    oBright = vec4(col * alpha * 5.0, alpha);
    oID = vec4(0);
}
