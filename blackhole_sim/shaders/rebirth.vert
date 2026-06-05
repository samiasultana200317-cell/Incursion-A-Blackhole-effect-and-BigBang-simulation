#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec4 aCol;
layout(location=2) in float aSize;
out vec4 vCol;
uniform mat4 uView, uProj;
void main() {
    vCol = aCol;
    gl_PointSize = aSize;
    gl_Position = uProj * uView * vec4(aPos, 1.0);
}
