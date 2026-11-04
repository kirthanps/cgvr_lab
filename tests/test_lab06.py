import unittest
import numpy as np
from lab_06.main import render,scene

class Depth(unittest.TestCase):
    def test_nearest_and_interpolation(self):
        far=(np.array([[0,0,.8],[10,0,.8],[0,10,.8]]),[0,0,1])
        near=(np.array([[0,0,.2],[10,0,.6],[0,10,.2]]),[1,0,0])
        c,z,o=render([far,near],12,12)
        self.assertAlmostEqual(z[1,1],.26)
        np.testing.assert_array_equal(c[1,1],[1,0,0]);self.assertEqual(o[1,1],1)
        self.assertTrue(np.isinf(z[11,11]))
    def test_order_winding_and_degenerate(self):
        tris=scene();a,z,_=render(tris);b,w,_=render(tris[::-1]);np.testing.assert_allclose(a,b);np.testing.assert_allclose(z,w)
        rev=[(v[::-1],c) for v,c in tris];b,w,_=render(rev);np.testing.assert_allclose(a,b);np.testing.assert_allclose(z,w,atol=1e-12)
        _,d,_=render([(np.array([[0,0,0],[1,1,0],[2,2,0]]),[1,0,0])],4,4)
        self.assertTrue(np.isinf(d).all())
    def test_equal_depth_keeps_first(self):
        v=np.array([[-10,-10,.5],[20,-10,.5],[-10,20,.5]])
        c,_,_=render([(v,[1,0,0]),(v,[0,1,0])],4,4)
        np.testing.assert_array_equal(c[1,1],[1,0,0])
