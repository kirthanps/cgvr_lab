"""Integration checks that require an actual OpenGL context, enabled explicitly."""
import os
import unittest
import numpy as np


@unittest.skipUnless(os.environ.get('CG_GL_TEST')=='1','Set CG_GL_TEST=1 and CG_HEADLESS=1 on Linux to execute actual OpenGL checks')
class OpenGLIntegration(unittest.TestCase):
    def test_gl_points_reach_framebuffer(self):
        from common.gl_runtime import Context
        from lab_01.main import bresenham
        with Context(64,64,headless=True) as ctx:
            g=ctx.gl;g.glViewport(0,0,64,64);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(0,64,0,64,-1,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
            # Offset integer coordinates to address exact framebuffer pixel centers.
            pts=bresenham(5,8,55,38);ctx.points([(x+.5,y+.5) for x,y in pts],(1,0,0),size=1)
            im=np.flipud(np.asarray(ctx.image()))
            for x,y in pts:np.testing.assert_array_equal(im[y,x],[255,0,0])
            ctx.check();self.assertGreaterEqual(ctx.info['depth_bits'],24)

    def test_actual_depth_against_independent_cpu_buffer(self):
        from lab_06.main import render,opengl_render,scene
        _,cpu,_=render(scene());color,depth,_=opengl_render(scene());reverse,rdepth,_=opengl_render(scene()[::-1])
        valid=np.isfinite(cpu)&(depth<1)
        self.assertGreater(valid.sum(),20000)
        np.testing.assert_allclose(depth[valid],cpu[valid],atol=2e-6)
        np.testing.assert_array_equal(color,reverse);np.testing.assert_allclose(depth,rdepth,atol=2e-6)

    def test_glsl_phong_matches_known_planar_sample(self):
        from common.gl_runtime import Context
        from lab_07.main import compile_phong,uniforms,phong
        with Context(65,65,headless=True) as ctx:
            g=ctx.gl;program=compile_phong(ctx)
            try:
                g.glViewport(0,0,65,65);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(-1,1,-1,1,-1,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
                g.glUseProgram(program);uniforms(ctx,program,light=(0,0,2),base=(.2,.4,.6),ka=.1,kd=.5,ks=.3)
                g.glBegin(g.GL_QUADS);g.glNormal3f(0,0,1)
                for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:g.glVertex3f(x,y,0)
                g.glEnd();g.glUseProgram(0)
                actual=np.asarray(ctx.image())[32,32]/255
                parts=phong([[0,0,0]],[[0,0,1]],light=(0,0,2),base=(.2,.4,.6),ka=.1,kd=.5,ks=.3)
                expected=sum(parts)[0]
                np.testing.assert_allclose(actual,expected,atol=1/255)
                ctx.check()
            finally:g.glDeleteProgram(program)
