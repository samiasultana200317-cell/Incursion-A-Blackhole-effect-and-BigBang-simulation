#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in float vAlpha;
in vec3 vNormal;

uniform vec3 uSunDir;
uniform vec3 uSunCol;
uniform int uObjectID;

void main() {
    float diff = max(dot(normalize(vNormal), normalize(uSunDir)), 0.2);
    vec3 baseColor = vec3(0.6, 0.4, 0.4) * diff * uSunCol;
    float heat = (1.0 - vAlpha) * 3.0;
    vec3 result = baseColor + vec3(1.0, 0.5, 0.1) * heat;
    
    oColor = vec4(result, vAlpha);
    oBright = vec4(result * heat, vAlpha);
    oID = vec4(float(uObjectID) / 10.0, 0, 0, 1.0);
}
