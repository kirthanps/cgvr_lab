"""Lab 2: midpoint circle/ellipse, polar comparison and supersampling."""
import argparse
import csv
import math
from time import perf_counter
import numpy as np
from common.gl_runtime import Context, output_dir, arguments, save_gif
from lab_01.main import round_pixel,styled


def midpoint_circle(cx,cy,r):
    if not isinstance(r,int) or r<0:
        raise ValueError('Radius must be a nonnegative integer')
    x,y,d=0,r,1-r
    result=set()
    while x<=y:
        result.update((cx+u,cy+v) for u,v in ((x,y),(-x,y),(x,-y),(-x,-y),(y,x),(-y,x),(y,-x),(-y,-x)))
        x+=1
        if d<0:
            d+=2*x+1
        else:
            y-=1;d+=2*(x-y)+1
    return sorted(result)


def midpoint_ellipse(cx,cy,rx,ry):
    if any(not isinstance(r,int) or r<0 for r in (rx,ry)):
        raise ValueError('Radii must be nonnegative integers')
    if rx==0:return [(cx,cy+y) for y in range(-ry,ry+1)]
    if ry==0:return [(cx+x,cy) for x in range(-rx,rx+1)]
    x,y=0,ry;rx2,ry2=rx*rx,ry*ry;dx,dy=0,2*rx2*y
    d1=ry2-rx2*ry+.25*rx2;result=set()
    def emit():result.update((cx+sx*x,cy+sy*y) for sx in (-1,1) for sy in (-1,1))
    while dx<dy:
        emit();x+=1;dx+=2*ry2
        if d1<0:d1+=dx+ry2
        else:y-=1;dy-=2*rx2;d1+=dx-dy+ry2
    d2=ry2*(x+.5)**2+rx2*(y-1)**2-rx2*ry2
    while y>=0:
        emit();y-=1;dy-=2*rx2
        if d2>0:d2+=rx2-dy
        else:x+=1;dx+=2*ry2;d2+=dx-dy+rx2
    return sorted(result)


def polar_circle(cx,cy,r):
    if not isinstance(r,int) or r<0:raise ValueError('Invalid radius')
    n=max(1,math.ceil(2*math.pi*r))
    return sorted({(cx+round_pixel(r*math.cos(i*2*math.pi/n)),cy+round_pixel(r*math.sin(i*2*math.pi/n))) for i in range(n)})


def antialiased_circle(r,size=100,scale=4):
    """Rasterize a thick midpoint outline at high resolution, then area-average samples."""
    if r<0 or r+2>=size/2 or scale<1:raise ValueError('Circle must fit canvas; positive supersampling factor required')
    mask=np.ones((size*scale,size*scale),dtype=float)
    for x,y in styled(midpoint_circle(size*scale//2,size*scale//2,r*scale),width=scale):
        if 0<=x<size*scale and 0<=y<size*scale:mask[y,x]=0
    return mask.reshape(size,scale,size,scale).mean(axis=(1,3))


def gl_antialias(out,r=35):
    """Supersample points rendered by OpenGL, then area-average framebuffer samples."""
    from PIL import Image
    with Context(400,400) as ctx:
        g=ctx.gl;g.glViewport(0,0,400,400);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(0,400,0,400,-1,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
        ctx.points(styled(midpoint_circle(200,200,r*4),width=4),color=(0,0,0),size=1)
        high=ctx.image();low=high.resize((100,100),Image.Resampling.BOX);low.save(out/'antialiased_circle.png')
    return low


def demo(cx=15,cy=-10,r=35,show=False):
    out=output_dir(__file__)
    with Context(title='Lab 2 — Midpoint circles / PyOpenGL') as ctx:
        cases=[(f'Midpoint | center ({cx},{cy}), r={r}',midpoint_circle(cx,cy,r),(cx-r-5,cy-r-5,cx+r+5,cy+r+5)),
               ('Concentric midpoint circles',[p for rad in (15,25,35) for p in midpoint_circle(0,0,rad)],(-45,-45,45,45)),
               ('Midpoint ellipse | two regions',midpoint_ellipse(0,0,45,25),(-55,-40,55,40))]
        for i,(title,pts,bounds) in enumerate(cases):ctx.panel(i,3,2,bounds,title);ctx.points(pts)
        ctx.panel(3,3,2,(-80,-45,80,55),'Five rings | midpoint GL_POINTS')
        for x,y,col in [(-44,15,(0,.52,.78)),(0,15,(.1,.1,.1)),(44,15,(.87,0,.14)),(-22,-10,(.85,.65,0)),(22,-10,(0,.62,.24))]:ctx.points(midpoint_circle(x,y,23),col,3)
        ctx.panel(4,3,2,(-45,-45,45,45),'Polar | trigonometric samples');ctx.points(polar_circle(0,0,35))
        ctx.panel(5,3,2,(-45,-45,45,45),'Midpoint | smooth OpenGL points')
        g=ctx.gl;g.glEnable(g.GL_POINT_SMOOTH);g.glEnable(g.GL_BLEND);g.glBlendFunc(g.GL_SRC_ALPHA,g.GL_ONE_MINUS_SRC_ALPHA);ctx.points(midpoint_circle(0,0,35),size=3);g.glDisable(g.GL_POINT_SMOOTH);g.glDisable(g.GL_BLEND)
        ctx.save(out/'circles.png');ctx.metadata(out);ctx.hold()
    gl_antialias(out)
    rows=[]
    for rad in (10,25,50,100,250):
        for fn in (midpoint_circle,polar_circle):
            start=perf_counter()
            for _ in range(100):pts=fn(0,0,rad)
            rows.append({'algorithm':fn.__name__,'radius':rad,'unique_pixels':len(pts),'mean_seconds':(perf_counter()-start)/100,'repeats':100})
    with (out/'benchmark.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    with Context(400,400,title='Lab 2 — growing OpenGL circle') as ctx:
        frames=[]
        for rad in range(0,46,2):
            ctx.clear();ctx.panel(0,1,1,(-50,-50,50,50),f'Midpoint growing circle | radius {rad}');ctx.points(midpoint_circle(0,0,rad),size=3);frames.append(ctx.image())
        save_gif(frames,out/'growing_circle.gif',100)
        def animate(t):
            rad=int(t*16)%46;ctx.clear();ctx.panel(0,1,1,(-50,-50,50,50),f'Growing circle | radius {rad}');ctx.points(midpoint_circle(0,0,rad),size=3)
        ctx.hold(animate)
    print('Lab 2 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--center',nargs=2,type=int,default=[15,-10]);p.add_argument('--radius',type=int,default=35);a=p.parse_args()
    if a.radius<0:p.error('--radius must be nonnegative')
    demo(*a.center,a.radius,a.show)
