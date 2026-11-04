"""Column-vector convention: p' = M @ p; listed transforms apply left-to-right."""
import math
import numpy as np


def translation(tx,ty):return np.array([[1,0,tx],[0,1,ty],[0,0,1.]],float)
def rotation(degrees):
    a=math.radians(degrees);c,s=math.cos(a),math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def scaling(sx,sy):return np.diag([sx,sy,1.])
def shear(shx=0,shy=0):return np.array([[1,shx,0],[shy,1,0],[0,0,1.]],float)
def reflection(axis='x'):
    choices={'x':scaling(1,-1),'y':scaling(-1,1),'origin':scaling(-1,-1),'y=x':np.array([[0,1,0],[1,0,0],[0,0,1.]])}
    if axis not in choices:raise ValueError('Reflection axis must be x, y, origin, or y=x')
    return choices[axis]
def compose(*matrices):
    result=np.eye(3)
    for m in matrices:result=np.asarray(m)@result
    return result
def about(matrix,pivot):
    x,y=pivot
    return compose(translation(-x,-y),matrix,translation(x,y))
def apply(points,matrix):
    pts=np.asarray(points,dtype=float);m=np.asarray(matrix,dtype=float)
    if pts.ndim!=2 or pts.shape[1]!=2 or m.shape!=(3,3):raise ValueError('Expected Nx2 points and 3x3 matrix')
    if not np.isfinite(pts).all() or not np.isfinite(m).all():raise ValueError('Coordinates and matrix must be finite')
    h=np.column_stack([pts,np.ones(len(pts))]);q=(m@h.T).T
    if np.any(np.isclose(q[:,2],0)):raise ValueError('Point mapped to infinity')
    return q[:,:2]/q[:,2,None]
