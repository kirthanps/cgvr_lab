"""Lab 6: software triangle rasterization and per-pixel Z-buffer visibility."""
import argparse
import json
import math
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from common.display import output_dir,save


def render(triangles,width=256,height=256,depth_test=True):
    """Input: (3x3 screen-space xyz vertices, RGB in [0,1]); smaller z is nearer.

    Orthographic projection is assumed. At each pixel center interpolate z with
    barycentric weights; update color and depth only when the sample is nearer.
    """
    if width<1 or height<1:raise ValueError('Positive framebuffer dimensions required')
    depth=np.full((height,width),np.inf);color=np.ones((height,width,3))*.96;owner=np.full((height,width),-1,int)
    for index,(vertices,rgb) in enumerate(triangles):
        v=np.asarray(vertices,float);rgb=np.asarray(rgb,float)
        if v.shape!=(3,3) or rgb.shape!=(3,) or not np.isfinite(v).all() or not np.isfinite(rgb).all():raise ValueError('Finite 3x3 vertices and RGB required')
        if np.any(rgb<0) or np.any(rgb>1):raise ValueError('RGB outside [0,1]')
        x0,y0=v[0,:2];x1,y1=v[1,:2];x2,y2=v[2,:2]
        denom=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(denom)<1e-12:continue
        xmin=max(0,math.floor(v[:,0].min()));xmax=min(width-1,math.ceil(v[:,0].max()))
        ymin=max(0,math.floor(v[:,1].min()));ymax=min(height-1,math.ceil(v[:,1].max()))
        if xmin>xmax or ymin>ymax:continue
        yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];px,py=xx+.5,yy+.5
        a=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/denom
        b=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/denom;c=1-a-b
        z=a*v[0,2]+b*v[1,2]+c*v[2,2]
        inside=(a>=-1e-12)&(b>=-1e-12)&(c>=-1e-12)
        view=depth[ymin:ymax+1,xmin:xmax+1]
        mask=inside & (z<view) if depth_test else inside
        view[mask]=z[mask];color[ymin:ymax+1,xmin:xmax+1][mask]=rgb;owner[ymin:ymax+1,xmin:xmax+1][mask]=index
    return color,depth,owner


def scene():
    # Intersecting slanted surfaces: no one global face order can resolve visibility.
    return [(np.array([[25,30,.15],[230,40,.9],[120,235,.55]]),[.13,.57,.72]),
            (np.array([[30,190,.8],[220,200,.15],[140,15,.65]]),[.92,.37,.25]),
            (np.array([[5,105,.48],[250,105,.48],[128,180,.48]]),[.85,.69,.20])]


def demo(show=False):
    out=output_dir(__file__);tris=scene();color,depth,owner=render(tris);reverse,revdepth,_=render(list(reversed(tris)))
    np.testing.assert_allclose(color,reverse);np.testing.assert_allclose(depth,revdepth)
    painter,_,_=render(tris,depth_test=False)
    Image.fromarray((np.flipud(color)*255).astype('uint8')).save(out/'zbuffer_color.png')
    np.save(out/'depth.npy',depth);np.save(out/'object_ids.npy',owner)
    fig,axes=plt.subplots(1,3,figsize=(13,4.5))
    axes[0].imshow(painter,origin='lower');axes[0].set_title('Without depth test | last submitted wins')
    axes[1].imshow(color,origin='lower');axes[1].set_title('Z-buffer | nearest surface per pixel')
    im=axes[2].imshow(np.ma.masked_invalid(depth),origin='lower',cmap='viridis_r',vmin=0,vmax=1);axes[2].set_title('Depth | smaller is nearer');fig.colorbar(im,ax=axes[2],shrink=.8,label='z')
    for ax in axes:ax.set(xlabel='screen x',ylabel='screen y')
    save(fig,out/'visibility.png',show)
    y,x=130,128
    (out/'results.json').write_text(json.dumps({'width':256,'height':256,'projection':'orthographic; pixel centers (x+0.5,y+0.5)',
        'near_rule':'smaller z wins; equal depths retain first submitted sample',
        'order_invariant_for_demo':bool(np.allclose(color,reverse)),
        'covered_pixels':int(np.isfinite(depth).sum()),'probe':{'x':x,'y':y,'depth':float(depth[y,x]),'triangle_index':int(owner[y,x]),'rgb':color[y,x].tolist()}},indent=2))
    print('Lab 6 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--show',action='store_true');demo(p.parse_args().show)
