#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 vFragPos;

uniform mat4 uModel, uView, uProj;

void main() {
    vFragPos = vec3(uModel * vec4(aPos, 1.0));
    gl_Position = uProj * uView * vec4(vFragPos, 1.0);
}
