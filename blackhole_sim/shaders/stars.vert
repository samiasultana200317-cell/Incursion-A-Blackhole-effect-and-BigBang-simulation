#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in float aBrightness;

out float vBrightness;

uniform mat4 uView, uProj;

void main() {
    vBrightness = aBrightness;
    gl_Position = uProj * uView * vec4(aPos, 1.0);
}
