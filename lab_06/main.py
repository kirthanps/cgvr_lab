"""Lab 6: software triangle rasterization and per-pixel Z-buffer visibility."""
import argparse
import json
import math
import numpy as np
from PIL import Image
from common.gl_runtime import Context,output_dir,arguments


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


def draw_triangles(ctx,triangles,depth_test=True):
    """Submit geometry, not a precomputed image. GL performs coverage and depth testing."""
    g=ctx.gl;g.glClear(g.GL_DEPTH_BUFFER_BIT);g.glUseProgram(0)
    if depth_test:g.glEnable(g.GL_DEPTH_TEST);g.glDepthFunc(g.GL_LESS)
    else:g.glDisable(g.GL_DEPTH_TEST)
    g.glBegin(g.GL_TRIANGLES)
    for vertices,rgb in triangles:
        g.glColor3f(*rgb)
        for x,y,z in vertices:g.glVertex3f(float(x),float(y),-float(z))
    g.glEnd();g.glDisable(g.GL_DEPTH_TEST)


def opengl_render(triangles,width=256,height=256):
    """Exact screen-space GL rendering for independent CPU/GL depth comparison."""
    with Context(width,height,title='Z-buffer framebuffer') as ctx:
        g=ctx.gl;g.glViewport(0,0,width,height);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(0,width,0,height,0,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
        draw_triangles(ctx,triangles);g.glFinish()
        color=np.frombuffer(g.glReadPixels(0,0,width,height,g.GL_RGB,g.GL_UNSIGNED_BYTE),dtype=np.uint8).reshape(height,width,3).astype(float)/255
        depth=np.asarray(g.glReadPixels(0,0,width,height,g.GL_DEPTH_COMPONENT,g.GL_FLOAT),dtype=np.float32).reshape(height,width).copy()
        ctx.check();return color,depth,ctx.info


def demo(show=False):
    out=output_dir(__file__);tris=scene();cpu,cpu_depth,owner=render(tris)
    glcolor,depth,info=opengl_render(tris);reverse,reverse_depth,_=opengl_render(list(reversed(tris)))
    np.testing.assert_allclose(glcolor,reverse,atol=1/255);np.testing.assert_allclose(depth,reverse_depth,atol=1e-6)
    covered=depth<1;both=covered&np.isfinite(cpu_depth)
    max_error=float(np.max(np.abs(depth[both]-cpu_depth[both])))
    if max_error>2e-6:raise AssertionError(f'CPU/OpenGL depth mismatch: {max_error}')
    Image.fromarray((np.flipud(glcolor)*255).astype('uint8')).save(out/'zbuffer_color.png')
    np.save(out/'depth.npy',depth);np.save(out/'depth_reference.npy',cpu_depth);np.save(out/'object_ids.npy',owner)
    with Context(1200,460,title='Lab 6 — actual OpenGL depth buffer') as ctx:
        ctx.panel(0,3,1,(0,0,256,256),'Depth test OFF | submission order',depth=True);draw_triangles(ctx,tris,False)
        ctx.panel(1,3,1,(0,0,256,256),'Depth test ON | GL_LESS',depth=True);draw_triangles(ctx,tris,True)
        ctx.panel(2,3,1,(0,0,256,256),'glReadPixels depth | blue=near',depth=True)
        g=ctx.gl;g.glPointSize(2);g.glBegin(g.GL_POINTS)
        for y,x in np.argwhere(covered):
            z=float(depth[y,x]);g.glColor3f(z,.65*(1-z)+.12,1-z);g.glVertex2f(x+.5,y+.5)
        g.glEnd();ctx.save(out/'visibility.png');ctx.metadata(out);ctx.hold()
    y,x=130,128
    (out/'results.json').write_text(json.dumps({'projection':'orthographic; smaller z is nearer','near_rule':'GL_DEPTH_TEST with GL_LESS; clear depth 1.0',
        'covered_pixels':int(covered.sum()),'cpu_gl_common_pixels':int(both.sum()),'maximum_cpu_gl_depth_error':max_error,
        'coverage_difference_pixels':int(np.count_nonzero(covered!=np.isfinite(cpu_depth))),
        'reversed_submission_order_matches':bool(np.allclose(glcolor,reverse,atol=1/255)),
        'probe':{'x':x,'y':y,'gl_depth':float(depth[y,x]),'cpu_depth':float(cpu_depth[y,x]),'gl_rgb':glcolor[y,x].tolist()},'context':info},indent=2))
    print('Lab 6 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));a=p.parse_args();demo(a.show)
