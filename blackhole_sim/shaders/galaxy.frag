#version 330 core
in float vBright;
in vec3 vCol;
layout(location=0) out vec4 oColor;
layout(location=1) out vec4 oBright;
layout(location=2) out vec4 oID;

void main() {
    vec2 pc = gl_PointCoord * 2.0 - 1.0;
    float d = dot(pc, pc);
    if(d > 1.0) discard;
    float a = exp(-d * 3.0);
    oColor = vec4(vCol * a, a);
    oBright = vec4(vCol * max(0.0, vBright - 0.5) * 2.0, 1.0);
    oID = vec4(0);
}
