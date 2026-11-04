import unittest,math
import numpy as np
from lab_02.main import midpoint_circle,midpoint_ellipse,antialiased_circle

class Circles(unittest.TestCase):
    def test_symmetry_and_radius(self):
        for r in range(41):
            pts=set(midpoint_circle(7,-3,r))
            self.assertIn((7+r,-3),pts)
            for x,y in pts:
                dx,dy=x-7,y+3
                self.assertIn((7-dy,-3+dx),pts)
                self.assertLessEqual(abs(math.hypot(dx,dy)-r),.71)
    def test_degenerate_and_ellipse(self):
        self.assertEqual(midpoint_circle(1,2,0),[(1,2)])
        self.assertEqual(len(midpoint_ellipse(0,0,0,3)),7)
        pts=set(midpoint_ellipse(0,0,30,15))
        for x,y in pts:
            self.assertIn((-x,y),pts);self.assertIn((x,-y),pts)
            self.assertLess(abs((x/30)**2+(y/15)**2-1),.09)
        with self.assertRaises(ValueError):midpoint_circle(0,0,-1)
    def test_antialias_coverage(self):
        a=antialiased_circle(35)
        self.assertTrue(np.any((a>0)&(a<1)))
        self.assertEqual(a[50,50],1)
