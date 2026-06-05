#version 330 core
layout (location = 0) in vec3 aPos;

out float vDeform;
out vec3 vWorldPos;

uniform mat4 uModel, uView, uProj;
uniform vec3 uAttractors[8];
uniform float uMasses[8];
uniform int uNAttractors;
uniform float uGravityScale;

void main() {
    vec3 worldPos = vec3(uModel * vec4(aPos, 1.0));
    vec3 pos = worldPos;
    float totalDeform = 0.0;
    
    for(int i=0; i<uNAttractors; i++) {
        vec2 d = pos.xz - uAttractors[i].xz;
        float r = length(d);
        
        // Smooth funnel: deep well using 1/r with soft core
        // This creates the classic GR space-time depression shape
        float well = uGravityScale * uMasses[i] / (r + 0.3);
        totalDeform += well;
    }

    // Soft clamp for stability but allow deep wells
    totalDeform = min(totalDeform, 15.0);
    
    pos.y -= totalDeform;
    vDeform = clamp(totalDeform / 8.0, 0.0, 1.0);
    vWorldPos = pos;
    gl_Position = uProj * uView * vec4(pos, 1.0);
}
