#version 120
varying vec3 interpolatedColor;
uniform vec3 tint;
void main() {
    gl_FragColor = vec4(clamp(interpolatedColor * tint, 0.0, 1.0), 1.0);
}
