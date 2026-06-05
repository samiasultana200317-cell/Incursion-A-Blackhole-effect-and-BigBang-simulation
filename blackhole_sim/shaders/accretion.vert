#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in float aTemp;

out float vTemp;
out float vRadii;

uniform mat4 uView, uProj;
uniform float uRs;

void main() {
    vTemp = aTemp;
    vRadii = length(aPos);
    gl_Position = uProj * uView * vec4(aPos, 1.0);
    gl_PointSize = mix(2.0, 7.0, clamp(1.0 - vRadii/(uRs*6.0), 0.0, 1.0));
}
