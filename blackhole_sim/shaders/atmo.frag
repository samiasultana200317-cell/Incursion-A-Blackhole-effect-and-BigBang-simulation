#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in vec3 vFragPos;
in vec3 vNormal;

uniform vec3 uSunDir;
uniform vec3 uEarthPos;

void main() {
    vec3 norm = normalize(vNormal);
    vec3 lightDir = normalize(uSunDir);
    float diff = max(dot(norm, lightDir), 0.0);
    
    // Rayleigh scattering approximation
    float viewRay = dot(norm, normalize(vFragPos - uEarthPos));
    float atmo = pow(1.0 - max(viewRay, 0.0), 3.0) * diff;
    
    vec3 color = vec3(0.3, 0.6, 1.0) * atmo;
    
    oColor = vec4(color, atmo * 0.5);
    oBright = vec4(0.0);
    oID = vec4(0.0);
}
