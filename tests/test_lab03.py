import unittest
import numpy as np
from common.transforms import *

class Transforms(unittest.TestCase):
    def test_known_coordinates(self):
        p=[[2,1]]
        np.testing.assert_allclose(apply(p,translation(3,-2)),[[5,-1]])
        np.testing.assert_allclose(apply(p,rotation(90)),[[-1,2]],atol=1e-12)
        np.testing.assert_allclose(apply(p,reflection('y=x')),[[1,2]])
        np.testing.assert_allclose(apply(p,shear(2)),[[4,1]])
        np.testing.assert_allclose(apply(p,scaling(3,.5)),[[6,.5]])
    def test_pivot_and_inverse(self):
        p=np.array([[2.,1.],[-5,7],[0,0]])
        m=about(rotation(67),(2,1))
        np.testing.assert_allclose(apply([[2,1]],m),[[2,1]])
        np.testing.assert_allclose(apply(apply(p,m),np.linalg.inv(m)),p,atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(rotation(67)),1)
    def test_reject_nonfinite(self):
        with self.assertRaises(ValueError):apply([[float('nan'),2]],np.eye(3))
