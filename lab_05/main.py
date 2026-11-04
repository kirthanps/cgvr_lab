"""Lab 5: Cohen–Sutherland clipping with explicit region outcodes."""
import argparse
import json
import math
from common.gl_runtime import Context,output_dir,arguments,GRAY,TEAL

LEFT,RIGHT,BOTTOM,TOP=1,2,4,8


def outcode(x,y,rect):
    xmin,ymin,xmax,ymax=rect
    return (LEFT if x<xmin else RIGHT if x>xmax else 0) | (BOTTOM if y<ymin else TOP if y>ymax else 0)


def clip_line(p0,p1,rect):
    """Inclusive rectangle, tuple of clipped endpoints or None for rejection."""
    xmin,ymin,xmax,ymax=map(float,rect);x0,y0=map(float,p0);x1,y1=map(float,p1)
    if not all(map(math.isfinite,(xmin,ymin,xmax,ymax,x0,y0,x1,y1))):raise ValueError('Finite coordinates required')
    if xmin>=xmax or ymin>=ymax:raise ValueError('Rectangle must have positive width and height')
    while True:
        c0,c1=outcode(x0,y0,rect),outcode(x1,y1,rect)
        if not (c0|c1):return ((x0,y0),(x1,y1))
        if c0&c1:return None
        c=c0 or c1
        if c&TOP:
            x=x0+(x1-x0)*(ymax-y0)/(y1-y0);y=ymax
        elif c&BOTTOM:
            x=x0+(x1-x0)*(ymin-y0)/(y1-y0);y=ymin
        elif c&RIGHT:
            y=y0+(y1-y0)*(xmax-x0)/(x1-x0);x=xmax
        else:
            y=y0+(y1-y0)*(xmin-x0)/(x1-x0);x=xmin
        if c==c0:x0,y0=x,y
        else:x1,y1=x,y


def demo(show=False):
    out=output_dir(__file__);rect=(0,0,10,8)
    cases=[('Inside',(2,2),(8,6)),('Crossing',(-4,2),(14,7)),('Outside',(-3,10),(13,10)),
           ('Vertical',(5,-4),(5,12)),('Horizontal',(-4,4),(14,4)),('Boundary',(0,-3),(0,11)),
           ('Corner touch',(-3,3),(3,-3)),('Point',(7,3),(7,3)),('Steep',(-1,-5),(8,15))]
    data=[]
    with Context(1080,1080,title='Lab 5 — Cohen-Sutherland / PyOpenGL') as ctx:
        for i,(name,a,b) in enumerate(cases):
            result=clip_line(a,b,rect);ctx.panel(i,3,3,(-5,-6,15,16),name+(' | accept' if result is not None else ' | reject'))
            ctx.line([(0,0),(10,0),(10,8),(0,8)],(.3,.3,.3),1,closed=True)
            ctx.line([a,b],GRAY,1);ctx.points([a,b],GRAY,4)
            if result is not None:ctx.line(result,TEAL,3);ctx.points(result,TEAL,5)
            data.append({'case':name,'input':[a,b],'outcodes':[outcode(*a,rect),outcode(*b,rect)],'clipped':result})
        ctx.save(out/'clipping.png');ctx.metadata(out);ctx.hold()
    (out/'results.json').write_text(json.dumps({'rectangle':rect,'cases':data},indent=2))
    print('Lab 5 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--line',type=float,nargs=4);p.add_argument('--rect',type=float,nargs=4,default=[0,0,10,8]);a=p.parse_args()
    if a.line:
        try:print(json.dumps(clip_line(a.line[:2],a.line[2:],a.rect)))
        except ValueError as e:p.error(str(e))
    else:demo(a.show)
