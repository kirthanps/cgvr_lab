"""Lab 1: explicit DDA and integer Bresenham, including all eight octants."""
import argparse
import csv
import json
import math
import random
from time import perf_counter
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from common.display import output_dir, pixels, save


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
    out = output_dir(__file__)
    fig, axes = plt.subplots(2,3,figsize=(13,8))
    ends = [(45,18),(18,45),(-18,45),(-45,18),(-45,-18),(-18,-45),(18,-45),(45,-18)]
    for ax,fn in zip(axes[0,:2],(dda,bresenham)):
        pixels(ax,[p for end in ends for p in fn(0,0,*end)],fn.__name__+' | all eight octants')
    line = dda(0,0,65,30)
    pixels(axes[0,2],styled(line,'dashed'),'DDA | dashed')
    pixels(axes[1,0],styled(line,'dotted'),'DDA | dotted')
    pixels(axes[1,1],styled(bresenham(0,0,65,30),width=5),'Bresenham | width 5')
    house = [(0,0),(50,0),(50,35),(25,60),(0,35),(0,0),(0,35),(50,35)]
    detail = [(20,0),(20,23),(30,23),(30,0)]
    pixels(axes[1,2],polyline(house)+polyline(detail),'Connected segments | wireframe house')
    save(fig,out/'line_algorithms.png',show)
    rng=random.Random(4104)
    lines=[tuple(rng.randint(-500,500) for _ in range(4)) for _ in range(1000)]
    rows=[]
    for fn in (dda,bresenham):
        samples=[]
        for _ in range(5):
            start=perf_counter()
            count=sum(len(fn(*line)) for line in lines)
            samples.append(perf_counter()-start)
        rows.append({'algorithm':fn.__name__,'lines':1000,'pixels':count,'best_seconds':min(samples),
                     'mean_seconds':sum(samples)/len(samples),'repeats':5})
    with (out/'benchmark.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    pts=bresenham(10,10,110,65)
    frames=[]
    for n in range(1,len(pts)+1,3):
        im=Image.new('RGB',(480,320),'white');draw=ImageDraw.Draw(im)
        draw.text((12,10),'Bresenham: incremental pixel generation',fill='black')
        for x,y in pts[:n]:
            draw.rectangle((x*4,300-y*4,x*4+3,303-y*4),fill='#147d92')
        frames.append(im)
    frames.append(frames[-1].copy())
    # Include the exact final endpoint even when the stride does not divide the count.
    draw=ImageDraw.Draw(frames[-1]); x,y=pts[-1];draw.rectangle((x*4,300-y*4,x*4+3,303-y*4),fill='#147d92')
    frames[0].save(out/'line_animation.gif',save_all=True,append_images=frames[1:],duration=90,loop=0)
    (out/'results.json').write_text(json.dumps({'sample':bresenham(0,0,6,3),'benchmark':rows},indent=2))
    print('Lab 1 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--show',action='store_true');a=p.parse_args();demo(a.show)
