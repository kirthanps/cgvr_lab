import unittest
import numpy as np
from lab_05.main import clip_line,outcode


def reference(a,b,rect):
    # Independent parametric interval clipping oracle, not the outcode algorithm.
    a=np.array(a,float);b=np.array(b,float);d=b-a;lo,hi=0.,1.
    for i,(lower,upper) in enumerate(((rect[0],rect[2]),(rect[1],rect[3]))):
        if d[i]==0:
            if not lower<=a[i]<=upper:return None
        else:
            u,v=sorted(((lower-a[i])/d[i],(upper-a[i])/d[i]));lo=max(lo,u);hi=min(hi,v)
            if lo>hi:return None
    return (a+lo*d,a+hi*d)

class Clipping(unittest.TestCase):
    def test_special_cases(self):
        r=(0,0,10,8)
        self.assertEqual(clip_line((-3,4),(14,4),r),((0.,4.),(10.,4.)))
        self.assertEqual(clip_line((0,-3),(0,11),r),((0.,0.),(0.,8.)))
        self.assertIsNone(clip_line((-3,10),(13,10),r))
        self.assertEqual(clip_line((3,3),(3,3),r),((3.,3.),(3.,3.)))
        self.assertEqual(clip_line((-3,3),(3,-3),r),((0.,0.),(0.,0.)))
        with self.assertRaises(ValueError):clip_line((0,0),(1,1),(0,0,0,1))
    def test_independent_oracle(self):
        rng=np.random.default_rng(4104);r=(0,0,10,8)
        for a,b in rng.uniform(-20,20,(1000,2,2)):
            actual=clip_line(a,b,r);expected=reference(a,b,r)
            self.assertEqual(actual is None,expected is None)
            if expected is not None:np.testing.assert_allclose(actual,expected,atol=1e-10)
