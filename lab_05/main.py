"""Lab 5: Cohen–Sutherland clipping with explicit region outcodes."""
import argparse
import json
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from common.display import output_dir,save

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
    fig,axes=plt.subplots(3,3,figsize=(12,10));data=[]
    for ax,(name,a,b) in zip(axes.flat,cases):
        result=clip_line(a,b,rect);ax.add_patch(Rectangle((0,0),10,8,fill=False,edgecolor='#555555',lw=1.5))
        ax.plot([a[0],b[0]],[a[1],b[1]],'--o',c='#bbbbbb',lw=1,markersize=3,label='Input')
        if result:
            u,v=result;ax.plot([u[0],v[0]],[u[1],v[1]],'-o',c='#147d92',lw=3,markersize=4,label='Accepted')
        ax.set(title=name+(' | accept' if result else ' | reject'),xlim=(-5,15),ylim=(-6,16),aspect='equal');ax.grid(alpha=.2);ax.legend(fontsize=7)
        data.append({'case':name,'input':[a,b],'outcodes':[outcode(*a,rect),outcode(*b,rect)],'clipped':result})
    save(fig,out/'clipping.png',show);(out/'results.json').write_text(json.dumps({'rectangle':rect,'cases':data},indent=2))
    print('Lab 5 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--show',action='store_true');p.add_argument('--line',type=float,nargs=4,metavar=('X0','Y0','X1','Y1'));p.add_argument('--rect',type=float,nargs=4,default=[0,0,10,8],metavar=('XMIN','YMIN','XMAX','YMAX'));a=p.parse_args()
    if a.line:
        try:print(json.dumps(clip_line(a.line[:2],a.line[2:],a.rect)))
        except ValueError as e:p.error(str(e))
    else:demo(a.show)
