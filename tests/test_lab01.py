import unittest
from lab_01.main import dda,bresenham,styled

class Lines(unittest.TestCase):
    def test_every_small_integer_segment(self):
        for x in range(-8,9):
            for y in range(-8,9):
                for fn in (dda,bresenham):
                    pts=fn(0,0,x,y)
                    self.assertEqual(pts[0],(0,0));self.assertEqual(pts[-1],(x,y))
                    self.assertEqual(len(pts),max(abs(x),abs(y))+1)
                    for a,b in zip(pts,pts[1:]):
                        self.assertLessEqual(max(abs(a[0]-b[0]),abs(a[1]-b[1])),1)
                    if x or y:
                        for px,py in pts:
                            self.assertLessEqual(abs(y*px-x*py)/max(abs(x),abs(y)),.500001)
    def test_styles(self):
        pts=dda(0,0,20,0)
        self.assertEqual(len(styled(pts,'dotted')),5)
        self.assertEqual(len(styled([(0,0)],width=3)),9)
        self.assertEqual(bresenham(4,7,4,7),[(4,7)])
