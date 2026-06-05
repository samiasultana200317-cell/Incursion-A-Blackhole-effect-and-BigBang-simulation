#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in vec3 vFragPos;
in vec3 vNormal;
in vec2 vTexCoord;

uniform sampler2D uTex;
uniform int uObjectID;
uniform vec3 uSunDir;
uniform vec3 uSunCol;

void main() {
    vec3 norm = normalize(vNormal);
    vec3 lightDir = normalize(uSunDir);
    float diff = max(dot(norm, lightDir), 0.1);
    vec3 color = texture(uTex, vTexCoord).rgb * diff * uSunCol;
    
    // Moon specific: slightly darker
    color *= 0.8;
    
    oColor = vec4(color, 1.0);
    oID = vec4(float(uObjectID) / 10.0, 0, 0, 1.0);
    
    float lum = dot(color, vec3(0.2126, 0.7152, 0.0722));
    if(lum > 0.8) oBright = vec4(color, 1.0);
    else oBright = vec4(0, 0, 0, 1);
}
