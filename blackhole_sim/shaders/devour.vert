#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out float vAlpha;
out vec3 vNormal;

uniform mat4 uModel, uView, uProj;
uniform vec3 uBHPos;
uniform float uStretch;
uniform float uCompress;
uniform float uAlpha;
uniform float uAngleDrift;

void main() {
    vec3 worldPos = vec3(uModel * vec4(aPos, 1.0));
    vec3 toBH = normalize(uBHPos - worldPos);
    vec3 radial = dot(aPos, toBH) * toBH;
    vec3 lateral = aPos - radial;
    vec3 deformed = radial * uStretch + lateral * uCompress;
    
    float ca = cos(uAngleDrift); float sa = sin(uAngleDrift);
    vec3 spiraled = vec3(deformed.x*ca - deformed.z*sa, deformed.y, deformed.x*sa + deformed.z*ca);
    
    vAlpha = uAlpha;
    vNormal = mat3(uModel) * aNormal;
    gl_Position = uProj * uView * uModel * vec4(spiraled, 1.0);
}
