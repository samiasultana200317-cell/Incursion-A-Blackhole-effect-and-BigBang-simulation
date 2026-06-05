#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in float vBrightness;

void main() {
    float b = vBrightness * 0.8;
    oColor = vec4(b, b, b, 1.0);
    oBright = vec4(b * 2.0, b * 2.0, b * 2.0, 1.0);
    oID = vec4(0);
}
