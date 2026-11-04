import os
import unittest
import numpy as np
from lab_10.main import look_at,perspective,orthographic,viewport_map,clip_segment,stages,rotation_y,CUBE

class ViewingMath(unittest.TestCase):
    def test_camera_known_positions(self):
        view=look_at((0,0,5),(0,0,0))
        np.testing.assert_allclose(view@np.array([0,0,5,1]),[0,0,0,1])
        np.testing.assert_allclose(view@np.array([0,0,0,1]),[0,0,-5,1])
        np.testing.assert_allclose(view[:3,:3]@view[:3,:3].T,np.eye(3),atol=1e-12)
    def test_projection_and_viewport(self):
        for p in [perspective(90,1,1,10),orthographic(-2,2,-2,2,1,10)]:
            for z,expected in [(-1,-1),(-10,1)]:
                clip=p@np.array([0,0,z,1]);self.assertAlmostEqual(clip[2]/clip[3],expected)
        np.testing.assert_allclose(viewport_map([[-1,-1,-1],[0,0,0],[1,1,1]],(10,20,200,100)),[[10,20,0],[110,70,.5],[210,120,1]])
        p=perspective(90,1,1,10);a=p@np.array([1,0,-2,1]);b=p@np.array([1,0,-4,1]);self.assertAlmostEqual(a[0]/a[3],2*b[0]/b[3])
    def test_homogeneous_clipping(self):
        np.testing.assert_allclose(clip_segment([-2,0,0,1],[0,0,0,1]),[[-1,0,0,1],[0,0,0,1]])
        np.testing.assert_allclose(clip_segment([0,0,-2,1],[0,0,0,1]),[[0,0,-1,1],[0,0,0,1]])
        self.assertIsNone(clip_segment([2,0,0,1],[3,0,0,1]))
        self.assertIsNone(clip_segment([0,0,0,-1],[0,0,0,-2]))
        # A camera-plane crossing is clipped before division, never divided by zero.
        line=clip_segment([0,0,0,-1],[0,0,0,1]);self.assertTrue((line[:,3]>0).all())
    def test_invalid_parameters(self):
        for args in [(0,1,1,10),(90,0,1,10),(90,1,0,10),(90,1,2,1)]:
            with self.assertRaises(ValueError):perspective(*args)
        with self.assertRaises(ValueError):look_at((0,0,0),(0,0,0))
        with self.assertRaises(ValueError):look_at((0,1,0),(0,0,0),(0,1,0))
    def test_stage_composition(self):
        model=rotation_y(30);view=look_at((4,3,6),(0,0,0));p=perspective(50,1,.5,30)
        data=stages(CUBE,model,view,p,(0,0,500,500));h=np.column_stack([CUBE,np.ones(8)])
        np.testing.assert_allclose(data['clip'],(p@view@model@h.T).T,atol=1e-12)
        self.assertTrue(data['visible'].all())

@unittest.skipUnless(os.environ.get('CG_GL_TEST')=='1','Enable OpenGL integration with CG_GL_TEST=1')
class ViewingGL(unittest.TestCase):
    def test_predicted_viewport_positions_reach_real_framebuffer(self):
        from common.gl_runtime import Context
        from lab_08.main import ShaderMesh
        model=rotation_y(25);view=look_at((4,3,6),(0,0,0));vp=(13,17,220,190);p=perspective(50,vp[2]/vp[3],.5,30)
        projected=stages(CUBE,model,view,p,vp)['screen']
        vertices=np.column_stack([CUBE,np.tile([1,0,0],(8,1))]).astype(np.float32)
        with Context(256,240,headless=True) as ctx:
            ctx.gl.glViewport(*vp);ctx.gl.glPointSize(3)
            with ShaderMesh(ctx,vertices,ctx.gl.GL_POINTS) as mesh:mesh.draw(p@view@model)
            image=np.flipud(np.asarray(ctx.image()))
            for x,y,z in projected:
                ix,iy=int(np.floor(x)),int(np.floor(y));patch=image[iy-2:iy+3,ix-2:ix+3]
                self.assertTrue(np.any(np.all(patch==[255,0,0],axis=2)),(x,y,z))
            ctx.check()
