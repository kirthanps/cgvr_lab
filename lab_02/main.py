"""Lab 2: midpoint circle/ellipse, polar comparison and supersampling."""
import argparse
import csv
import math
from time import perf_counter
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from common.display import output_dir,pixels,save
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


def demo(cx=15,cy=-10,r=35,show=False):
    out=output_dir(__file__)
    fig,ax=plt.subplots(2,3,figsize=(13,8))
    pixels(ax[0,0],midpoint_circle(cx,cy,r),f'Midpoint | center ({cx}, {cy}), r={r}')
    pixels(ax[0,1],[p for rad in (15,25,35) for p in midpoint_circle(0,0,rad)],'Concentric circles')
    pixels(ax[0,2],midpoint_ellipse(0,0,45,25),'Two-region midpoint ellipse')
    for x,y,col in [(-44,15,'#0085c7'),(0,15,'#333333'),(44,15,'#df0024'),(-22,-10,'#d8a500'),(22,-10,'#009f3d')]:
        pts=np.array(midpoint_circle(x,y,23));ax[1,0].scatter(pts[:,0],pts[:,1],s=9,c=col,marker='s')
    ax[1,0].set(title='Five-ring arrangement',aspect='equal');ax[1,0].grid(alpha=.2)
    pixels(ax[1,1],polar_circle(0,0,35),'Polar circle | trigonometric samples')
    aa=antialiased_circle(35)
    ax[1,2].imshow(aa,cmap='gray',vmin=0,vmax=1);ax[1,2].set_title('Midpoint | 4× supersampling');ax[1,2].axis('off')
    save(fig,out/'circles.png',show)
    Image.fromarray((aa*255).astype('uint8')).save(out/'antialiased_circle.png')
    rows=[]
    for rad in (10,25,50,100,250):
        for fn in (midpoint_circle,polar_circle):
            start=perf_counter()
            for _ in range(100):pts=fn(0,0,rad)
            rows.append({'algorithm':fn.__name__,'radius':rad,'unique_pixels':len(pts),'mean_seconds':(perf_counter()-start)/100,'repeats':100})
    with (out/'benchmark.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    frames=[]
    for rad in range(0,46,2):
        im=Image.new('RGB',(320,320),'white');draw=ImageDraw.Draw(im)
        draw.text((10,10),f'Midpoint growing circle: radius {rad}',fill='black')
        for x,y in midpoint_circle(0,0,rad):draw.rectangle((158+3*x,158-3*y,160+3*x,160-3*y),fill='#147d92')
        frames.append(im)
    frames[0].save(out/'growing_circle.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
    print('Lab 2 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--center',nargs=2,type=int,default=[15,-10]);p.add_argument('--radius',type=int,default=35);p.add_argument('--show',action='store_true');a=p.parse_args()
    if a.radius<0:p.error('--radius must be nonnegative')
    demo(*a.center,a.radius,a.show)
