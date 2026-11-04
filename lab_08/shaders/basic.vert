#version 120
attribute vec3 position;
attribute vec3 vertexColor;
uniform mat4 mvp;
varying vec3 interpolatedColor;
void main() {
    gl_Position = mvp * vec4(position, 1.0);
    interpolatedColor = vertexColor;
}
