import os
import unittest
import numpy as np
from lab_08.main import TRIANGLE,rotation_z

class ShaderMath(unittest.TestCase):
    def test_rotation_and_inverse(self):
        m=rotation_z(90);np.testing.assert_allclose(m@np.array([1,0,0,1]),[0,1,0,1],atol=1e-6)
        np.testing.assert_allclose(rotation_z(-37)@rotation_z(37),np.eye(4),atol=1e-6)

@unittest.skipUnless(os.environ.get('CG_GL_TEST')=='1','Enable actual OpenGL integration checks with CG_GL_TEST=1')
class BasicShaderGL(unittest.TestCase):
    def test_interpolated_color_and_tint(self):
        from common.gl_runtime import Context
        from lab_08.main import ShaderMesh
        # The center of an odd-sized viewport is exactly NDC (0,0).
        xy=TRIANGLE[:,:2].T.astype(float)
        weights=np.linalg.solve(np.vstack([xy,np.ones(3)]),[0,0,1])
        expected=weights@TRIANGLE[:,3:]
        with Context(65,65,headless=True) as ctx:
            ctx.gl.glViewport(0,0,65,65)
            with ShaderMesh(ctx,TRIANGLE) as mesh:
                self.assertTrue(mesh.status['linked'])
                for tint in ((1,1,1),(.4,1,.7)):
                    ctx.clear();ctx.gl.glViewport(0,0,65,65);mesh.draw(tint=tint)
                    actual=np.asarray(ctx.image())[32,32]/255
                    np.testing.assert_allclose(actual,expected*np.asarray(tint),atol=1/255)
            ctx.check()
