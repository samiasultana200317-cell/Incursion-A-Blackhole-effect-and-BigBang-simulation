#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in vec3 vFragPos;
uniform vec3 uBHPos;
uniform float uRs;
uniform float uTime;
uniform int uObjectID;

void main() {
    vec3 toCenter = vFragPos - uBHPos;
    float r = length(toCenter);
    float nr = r / uRs;

    // Photon sphere ring (nr ≈ 1.5)
    float ring = smoothstep(1.35, 1.50, nr) - smoothstep(1.50, 1.65, nr);
    vec3 ringCol = vec3(1.0, 0.72, 0.28) * ring * 10.0;

    // Outer glow
    float glow = max(0.0, 1.0 - (nr - 1.0) / 1.5) * (1.0 - ring);
    glow = pow(glow, 4.0) * 0.6;
    vec3 glowCol = vec3(0.6, 0.4, 1.0) * glow;

    vec3 finalCol = ringCol + glowCol;
    
    // Event horizon: if we are inside Rs, pure black
    if (nr < 1.0) {
        oColor = vec4(0, 0, 0, 1);
        oBright = vec4(0, 0, 0, 1);
    } else {
        oColor = vec4(finalCol, 1.0);
        oBright = vec4(finalCol * 2.0, 1.0);
    }
    oID = vec4(float(uObjectID) / 10.0, 0, 0, 1.0);
}
