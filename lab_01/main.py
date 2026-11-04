"""Lab 1: explicit DDA and integer Bresenham, including all eight octants."""
import argparse
import csv
import json
import math
import random
from time import perf_counter
from common.gl_runtime import Context, output_dir, arguments, save_gif


def round_pixel(x):
    """Round half away from zero, avoiding Python's ties-to-even pixel convention."""
    return math.floor(x + .5) if x >= 0 else math.ceil(x - .5)


def dda(x0, y0, x1, y1):
    dx, dy = x1-x0, y1-y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    return [(round_pixel(x0+i*dx/steps), round_pixel(y0+i*dy/steps)) for i in range(steps+1)]


def bresenham(x0, y0, x1, y1):
    dx, dy = abs(x1-x0), -abs(y1-y0)
    sx, sy = (1 if x0<x1 else -1), (1 if y0<y1 else -1)
    err, points = dx+dy, []
    while True:
        points.append((x0, y0))
        if (x0,y0)==(x1,y1):
            return points
        e2 = 2*err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def styled(points, kind='solid', width=1):
    """Dash = six on/four off; dots = one on/four off; square raster brush."""
    if kind not in ('solid','dashed','dotted') or width < 1:
        raise ValueError('Choose solid/dashed/dotted and a positive width')
    keep = lambda i: kind=='solid' or (kind=='dashed' and i%10<6) or (kind=='dotted' and i%5==0)
    lo = -(width//2)
    return sorted({(x+ox,y+oy) for i,(x,y) in enumerate(points) if keep(i)
                   for ox in range(lo,lo+width) for oy in range(lo,lo+width)})


def polyline(vertices, algorithm=bresenham):
    return [p for a,b in zip(vertices,vertices[1:]) for p in algorithm(*a,*b)]


def demo(show=False):
    out=output_dir(__file__)
    ends=[(45,18),(18,45),(-18,45),(-45,18),(-45,-18),(-18,-45),(18,-45),(45,-18)]
    line=dda(0,0,65,30)
    house=[(0,0),(50,0),(50,35),(25,60),(0,35),(0,0),(0,35),(50,35)]
    cases=[('DDA | eight octants',[p for end in ends for p in dda(0,0,*end)],(-55,-55,55,55)),
           ('Bresenham | eight octants',[p for end in ends for p in bresenham(0,0,*end)],(-55,-55,55,55)),
           ('DDA | dashed',styled(line,'dashed'),(-5,-10,70,40)),
           ('DDA | dotted',styled(line,'dotted'),(-5,-10,70,40)),
           ('Bresenham | square brush width 5',styled(bresenham(0,0,65,30),width=5),(-5,-10,70,40)),
           ('Connected segments | house',polyline(house)+polyline([(20,0),(20,23),(30,23),(30,0)]),(-10,-5,60,65))]
    with Context(title='Lab 1 — DDA and Bresenham / PyOpenGL') as ctx:
        for i,(title,pts,bounds) in enumerate(cases):
            ctx.panel(i,3,2,bounds,title);ctx.axes(bounds);ctx.points(pts,size=2)
        ctx.save(out/'line_algorithms.png');ctx.metadata(out);ctx.hold()
    rng=random.Random(4104);lines=[tuple(rng.randint(-500,500) for _ in range(4)) for _ in range(1000)];rows=[]
    for fn in (dda,bresenham):
        times=[]
        for _ in range(5):
            start=perf_counter();count=sum(len(fn(*line)) for line in lines);times.append(perf_counter()-start)
        rows.append({'algorithm':fn.__name__,'lines':1000,'pixels':count,'best_seconds':min(times),'mean_seconds':sum(times)/5,'repeats':5})
    with (out/'benchmark.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    pts=bresenham(10,10,110,65);frames=[]
    with Context(600,360,title='Lab 1 — incremental OpenGL points') as ctx:
        for n in list(range(1,len(pts),3))+[len(pts)]:
            ctx.clear();ctx.panel(0,1,1,(0,0,120,75),f'Bresenham | {n}/{len(pts)} pixels');ctx.points(pts[:n],size=4);frames.append(ctx.image())
        save_gif(frames,out/'line_animation.gif')
        ctx.hold(lambda t: draw_animation(ctx,pts,t))
    (out/'results.json').write_text(json.dumps({'sample':bresenham(0,0,6,3),'benchmark':rows,'display':'GL_POINTS / framebuffer readback'},indent=2))
    print('Lab 1 OpenGL outputs:',out)


def draw_animation(ctx,pts,t):
    n=1+int(t*35)%len(pts);ctx.clear();ctx.panel(0,1,1,(0,0,120,75),'Bresenham | incremental rasterization');ctx.points(pts[:n],size=4)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));a=p.parse_args();demo(a.show)
