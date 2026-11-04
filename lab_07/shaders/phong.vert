#version 120
// Compatibility input attributes allow the geometry submission to remain readable.
varying vec3 worldPosition;
varying vec3 worldNormal;
void main() {
    worldPosition = gl_Vertex.xyz;
    worldNormal = gl_Normal;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
