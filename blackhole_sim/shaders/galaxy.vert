#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in float aBright;
out float vBright;
out vec3 vCol;
uniform mat4 uView, uProj;
uniform float uTime;
uniform vec3 uGalCenter;
uniform int uArmCount;

void main() {
    vBright = aBright;
    // Colour from brightness
    vCol = mix(vec3(0.3,0.4,0.8), vec3(1.0,0.95,0.7), aBright);
    gl_PointSize = mix(1.5, 4.0, aBright);
    gl_Position = uProj * uView * vec4(aPos, 1.0);
}
