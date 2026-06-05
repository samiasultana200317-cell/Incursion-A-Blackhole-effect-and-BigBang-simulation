#version 330 core
in vec4 vCol;
layout(location=0) out vec4 oColor;
layout(location=1) out vec4 oBright;
layout(location=2) out vec4 oID;
void main() {
    vec2 pc = gl_PointCoord * 2.0 - 1.0;
    float d = dot(pc, pc);
    if(d > 1.0) discard;
    float a = exp(-d * 2.5) * vCol.a;
    vec3 c = vCol.rgb;
    oColor = vec4(c * a, a);
    float lum = dot(c, vec3(0.299, 0.587, 0.114));
    oBright = vec4(c * max(0.0, lum - 0.4) * a * 2.0, 1.0);
    oID = vec4(0);
}
