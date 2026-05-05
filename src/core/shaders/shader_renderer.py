"""
shader_renderer.py  — drop this anywhere importable, e.g. src/shader_renderer.py

Wraps the PyOpenGL boilerplate so StateManager stays clean.
"""

import ctypes
import numpy as np
import pygame
from OpenGL.GL import *


# ─────────────────────────────────────────────────────────────────────────────
# GLSL source — edit FRAG_SRC to change the effect
# ─────────────────────────────────────────────────────────────────────────────

_VERT = """
#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUV;
out vec2 vUV;
void main() {
    vUV = aUV;
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

# ── Swap this block for any other effect you like ────────────────────────────
_FRAG = """
#version 330 core
in  vec2  vUV;
out vec4  FragColor;

uniform sampler2D uTex;
uniform float     uTime;
uniform vec2      uRes;

// ── Cheap 9-tap box blur for the bloom source ─────────────────────────────
vec3 blurSample(sampler2D tex, vec2 uv, float radius) {
    vec2 px = radius / uRes;
    vec3 acc = vec3(0.0);
    acc += texture(tex, uv + vec2(-px.x, -px.y)).rgb;
    acc += texture(tex, uv + vec2(  0.0, -px.y)).rgb;
    acc += texture(tex, uv + vec2( px.x, -px.y)).rgb;
    acc += texture(tex, uv + vec2(-px.x,   0.0)).rgb;
    acc += texture(tex, uv                      ).rgb;
    acc += texture(tex, uv + vec2( px.x,   0.0)).rgb;
    acc += texture(tex, uv + vec2(-px.x,  px.y)).rgb;
    acc += texture(tex, uv + vec2(  0.0,  px.y)).rgb;
    acc += texture(tex, uv + vec2( px.x,  px.y)).rgb;
    return acc / 9.0;
}

void main() {
    vec2 uv = vUV;

    // ── very gentle barrel warp (reduced from 0.035 → 0.010) ─────────────
    vec2 c = uv * 2.0 - 1.0;
    float d = dot(c, c);
    c *= 1.0 + d * 0.010;
    uv = c * 0.5 + 0.5;

    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // ── base colour ───────────────────────────────────────────────────────
    vec4 col = texture(uTex, uv);

    // ── bloom ─────────────────────────────────────────────────────────────
    // Extract bright areas, blur them, and add back on top.
    // Three passes at increasing radii give a soft halo.
    vec3 b1 = blurSample(uTex, uv,  2.5);
    vec3 b2 = blurSample(uTex, uv,  6.0);
    vec3 b3 = blurSample(uTex, uv, 12.0);

    // Only the bright parts bleed (anything above ~0.5 luminance)
    float lum1 = dot(b1, vec3(0.299, 0.587, 0.114));
    float lum2 = dot(b2, vec3(0.299, 0.587, 0.114));
    float lum3 = dot(b3, vec3(0.299, 0.587, 0.114));

    vec3 bloom = b1 * max(0.0, lum1 - 0.45) * 1.6
               + b2 * max(0.0, lum2 - 0.40) * 1.2
               + b3 * max(0.0, lum3 - 0.35) * 0.8;

    col.rgb += bloom;

    // ── subtle colour fringing on bright edges (replaces hard chroma ab.) ─
    float r = texture(uTex, uv + vec2( 0.0008, 0.0)).r;
    float b = texture(uTex, uv + vec2(-0.0008, 0.0)).b;
    col.r = mix(col.r, r, 0.5);
    col.b = mix(col.b, b, 0.5);

    // ── very faint scanlines — just a texture hint, not a CRT grid ────────
    float scan = sin(uv.y * uRes.y * 3.14159) * 0.5 + 0.5;
    col.rgb *= 0.96 + 0.04 * scan;

    // ── soft vignette ─────────────────────────────────────────────────────
    col.rgb *= 1.0 - d * 0.38;

    // ── gentle warm/cool grade — makes glows feel more filmic ────────────
    col.r *= 1.04;
    col.b *= 1.06;

    FragColor = vec4(col.rgb, 1.0);
}
"""
# ─────────────────────────────────────────────────────────────────────────────


def _compile(src: str, kind: int) -> int:
    s = glCreateShader(kind)
    glShaderSource(s, src)
    glCompileShader(s)
    if not glGetShaderiv(s, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(s).decode())
    return s


def _link(vert_src: str, frag_src: str) -> int:
    prog = glCreateProgram()
    v = _compile(vert_src, GL_VERTEX_SHADER)
    f = _compile(frag_src, GL_FRAGMENT_SHADER)
    glAttachShader(prog, v)
    glAttachShader(prog, f)
    glLinkProgram(prog)
    if not glGetProgramiv(prog, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(prog).decode())
    glDeleteShader(v)
    glDeleteShader(f)
    return prog


class ShaderRenderer:
    """
    Usage
    -----
    renderer = ShaderRenderer(width, height)

    # inside your loop, after every scene has drawn to `game_surface`:
    renderer.blit(game_surface, elapsed_time)
    pygame.display.flip()
    """

    def __init__(self, width: int, height: int) -> None:
        self.w = width
        self.h = height
        self._prog = _link(_VERT, _FRAG)

        # fullscreen quad  (x, y, u, v)
        verts = np.array([
            -1, -1,  0, 0,
             1, -1,  1, 0,
             1,  1,  1, 1,
            -1, -1,  0, 0,
             1,  1,  1, 1,
            -1,  1,  0, 1,
        ], dtype=np.float32)

        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        s = 4 * verts.itemsize
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

        # texture that receives the pygame surface pixels
        self._tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8,
                     width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        # cache uniform locations
        self._u_tex  = glGetUniformLocation(self._prog, "uTex")
        self._u_time = glGetUniformLocation(self._prog, "uTime")
        self._u_res  = glGetUniformLocation(self._prog, "uRes")

    # ── public API ────────────────────────────────────────────────────────────

    def blit(self, surface: pygame.Surface, elapsed: float = 0.0) -> None:
        """Upload *surface* to the GPU and draw it through the shader."""
        raw = pygame.image.tostring(surface, "RGBA", True)  # flip=True fixes Y

        glBindTexture(GL_TEXTURE_2D, self._tex)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0,
                        self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, raw)

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self._prog)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._tex)
        glUniform1i(self._u_tex,  0)
        glUniform1f(self._u_time, elapsed)
        glUniform2f(self._u_res,  float(self.w), float(self.h))

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

    def destroy(self) -> None:
        glDeleteVertexArrays(1, [self._vao])
        glDeleteBuffers(1, [self._vbo])
        glDeleteTextures(1, [self._tex])
        glDeleteProgram(self._prog)