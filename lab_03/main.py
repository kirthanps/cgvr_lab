"""Lab 3: 2D homogeneous transforms, pivot rotation and interactive menu."""
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from common.transforms import translation,rotation,scaling,reflection,shear,about,apply,compose
from common.display import output_dir,save

POLYGON=np.array([[-2,-1],[2,-1],[2,1],[0,3],[-2,1]],float)
COMPLEX=np.array([[-3,-2],[3,-2],[3,0],[1,0],[1,3],[-1,3],[-1,0],[-3,0]],float)


def draw_polygon(ax,p,label,color):
    q=np.vstack([p,p[0]])
    ax.plot(q[:,0],q[:,1],'-o',label=label,c=color,markersize=3)
    ax.set_aspect('equal');ax.grid(alpha=.25);ax.axhline(0,c='gray',lw=.5);ax.axvline(0,c='gray',lw=.5)


def rotation_animation(out,polygon=POLYGON):
    frames=[]
    for angle in range(0,360,10):
        p=apply(polygon,rotation(angle))
        im=Image.new('RGB',(400,400),'white');d=ImageDraw.Draw(im)
        d.line((0,200,400,200),fill='#bbbbbb');d.line((200,0,200,400),fill='#bbbbbb')
        d.polygon([(200+40*x,200-40*y) for x,y in p],fill='#c8e8ed',outline='#147d92',width=3)
        d.text((12,12),f'Continuous rotation | {angle} degrees',fill='black');frames.append(im)
    frames[0].save(out/'rotation.gif',save_all=True,append_images=frames[1:],duration=70,loop=0)


def demo(show=False):
    out=output_dir(__file__)
    cases={'Translate (4, 2)':translation(4,2),'Rotate 45 degrees':rotation(45),
           'Non-uniform scale (1.6, 0.6)':scaling(1.6,.6),'Reflect about y=x':reflection('y=x'),
           'Shear x by 0.8':shear(.8,0),'Rotate 60 around pivot (2, 1)':about(rotation(60),(2,1))}
    fig,axes=plt.subplots(2,3,figsize=(13,8));data={}
    for ax,(title,m) in zip(axes.flat,cases.items()):
        q=apply(POLYGON,m);data[title]={'matrix':m.tolist(),'vertices':q.tolist()}
        draw_polygon(ax,POLYGON,'Original','#888888');draw_polygon(ax,q,'Transformed','#147d92')
        if 'pivot' in title:ax.scatter([2],[1],c='#c64949',marker='x',label='Pivot')
        ax.set_title(title);ax.legend(fontsize=8)
    save(fig,out/'transformations.png',show)
    m=compose(scaling(1.2,.7),shear(.3),rotation(30),translation(3,1))
    fig,ax=plt.subplots(figsize=(7,5));draw_polygon(ax,COMPLEX,'Original','#888888');draw_polygon(ax,apply(COMPLEX,m),'Scale, shear, rotate, translate','#147d92');ax.legend();ax.set_title('Multiple transforms on a concave polygon');save(fig,out/'complex_polygon.png')
    data['complex_polygon']={'matrix':m.tolist(),'vertices':apply(COMPLEX,m).tolist()}
    (out/'coordinates.json').write_text(json.dumps(data,indent=2));rotation_animation(out)
    print('Lab 3 outputs:',out)


def menu():
    """Terminal interaction works on desktops and without a GUI event loop."""
    points=POLYGON.copy();out=output_dir(__file__)
    while True:
        print('\n1 translate | 2 rotate about pivot | 3 scale | 4 reflect | 5 shear | 6 reset | 0 quit')
        try:
            choice=input('Choice: ').strip()
            if choice=='0':return
            if choice=='6':points=POLYGON.copy();continue
            if choice=='1':m=translation(*map(float,input('tx ty: ').split()))
            elif choice=='2':
                a,x,y=map(float,input('degrees pivot_x pivot_y: ').split());m=about(rotation(a),(x,y))
            elif choice=='3':m=scaling(*map(float,input('sx sy: ').split()))
            elif choice=='4':m=reflection(input('x / y / origin / y=x: ').strip())
            elif choice=='5':m=shear(*map(float,input('shx shy: ').split()))
            else:print('Unknown choice');continue
            new=apply(points,m);fig,ax=plt.subplots(figsize=(7,6));draw_polygon(ax,points,'Before','#888888');draw_polygon(ax,new,'After','#147d92');ax.legend();ax.set_title('Interactive transformation');save(fig,out/'interactive.png');points=new
            print('Matrix:\n',m,'\nVertices:\n',points,'\nSaved',out/'interactive.png')
        except (ValueError,TypeError) as e:print('Invalid input:',e)
        except EOFError:return


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--menu',action='store_true');p.add_argument('--show',action='store_true');a=p.parse_args();menu() if a.menu else demo(a.show)
