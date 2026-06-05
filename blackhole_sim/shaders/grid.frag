#version 330 core
layout (location = 0) out vec4 oColor;
layout (location = 1) out vec4 oBright;
layout (location = 2) out vec4 oID;

in float vDeform;
in vec3 vWorldPos;

uniform float uOpacity;

void main() {
    // Classic cyan space-time grid matching GR visualizations
    vec3 cyan = vec3(0.0, 0.85, 0.95);
    
    // Slightly brighter near curvature for subtle depth cue
    vec3 col = cyan * (1.0 + vDeform * 0.4);
    
    // Distance fade at edges for clean look
    float dist = length(vWorldPos.xz);
    float edge_fade = smoothstep(13.0, 9.0, dist);
    
    float alpha = uOpacity * edge_fade;
    
    // Subtle bloom glow on the grid lines
    float bloom = 0.15 + vDeform * 0.3;
    
    oColor = vec4(col, alpha);
    oBright = vec4(col * bloom, alpha);
    oID = vec4(0);
}
