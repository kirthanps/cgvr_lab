import unittest
import numpy as np
from lab_07.main import phong,sphere

class Phong(unittest.TestCase):
    def test_front_and_back_light(self):
        p=np.array([[0.,0.,0.]]);n=np.array([[0.,0.,1.]])
        a,d,s=phong(p,n,light=(0,0,2),eye=(0,0,3),base=(.2,.4,.6),ka=.1,kd=.5,ks=.3)
        np.testing.assert_allclose(a,[[.02,.04,.06]]);np.testing.assert_allclose(d,[[.1,.2,.3]]);np.testing.assert_allclose(s,[[.3,.3,.3]])
        a,d,s=phong(p,n,light=(0,0,-2));np.testing.assert_array_equal(d,[[0,0,0]]);np.testing.assert_array_equal(s,[[0,0,0]])
    def test_shininess_and_normalization(self):
        p=np.array([[0.,0.,0.]]);n=np.array([[0.,0.,10.]])
        low=phong(p,n,light=(1,0,2),shininess=8)[2]
        high=phong(p,n,light=(1,0,2),shininess=128)[2]
        self.assertTrue(np.all(high<low))
        np.testing.assert_allclose(low,phong(p,n/10,light=(1,0,2),shininess=8)[2])
    def test_finite_sphere_and_validation(self):
        images,mask=sphere(64)
        self.assertTrue(mask.any())
        for im in images:self.assertTrue(np.isfinite(im).all());self.assertTrue(((im>=0)&(im<=1)).all())
        with self.assertRaises(ValueError):phong([[0,0,0]],[[0,0,0]])
        with self.assertRaises(ValueError):phong([[0,0,0]],[[0,0,1]],shininess=0)
