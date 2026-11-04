import unittest
import numpy as np
from common.transforms import *

class Composite(unittest.TestCase):
    def test_sequential_equivalence(self):
        rng=np.random.default_rng(4104);p=rng.normal(size=(50,2))
        steps=[scaling(2,.5),shear(.3),about(rotation(47),(2,1)),reflection('y=x'),translation(4,-2)]
        q=p.copy()
        for m in steps:q=apply(q,m)
        np.testing.assert_allclose(apply(p,compose(*steps)),q,atol=1e-12)
    def test_order_matters(self):
        a=apply([[1,0]],compose(rotation(90),translation(2,0)))
        b=apply([[1,0]],compose(translation(2,0),rotation(90)))
        np.testing.assert_allclose(a,[[2,1]],atol=1e-12)
        np.testing.assert_allclose(b,[[0,3]],atol=1e-12)
