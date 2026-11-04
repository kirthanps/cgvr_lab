#version 120
varying vec3 worldPosition;
varying vec3 worldNormal;
uniform vec3 lightPosition;
uniform vec3 eyePosition;
uniform vec3 baseColor;
uniform float ka;
uniform float kd;
uniform float ks;
uniform float shininess;
uniform int component;
void main() {
    vec3 N = normalize(worldNormal);
    vec3 L = normalize(lightPosition - worldPosition);
    vec3 V = normalize(eyePosition - worldPosition);
    float nDotL = dot(N, L);
    vec3 R = reflect(-L, N);
    vec3 ambient = ka * baseColor;
    vec3 diffuse = kd * baseColor * max(nDotL, 0.0);
    vec3 specular = vec3(0.0);
    if (nDotL > 0.0) {
        specular = vec3(ks * pow(max(dot(R, V), 0.0), shininess));
    }
    vec3 color = ambient + diffuse + specular;
    if (component == 0) color = ambient;
    else if (component == 1) color = diffuse;
    else if (component == 2) color = specular;
    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
