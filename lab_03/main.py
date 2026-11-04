"""Lab 3: homogeneous 2D transformations displayed in real OpenGL."""
import argparse
import json
import numpy as np
from common.transforms import translation,rotation,scaling,reflection,shear,about,apply,compose
from common.gl_runtime import Context,output_dir,arguments,save_gif,TEAL,GRAY

POLYGON=np.array([[-2,-1],[2,-1],[2,1],[0,3],[-2,1]],float)
COMPLEX=np.array([[-3,-2],[3,-2],[3,0],[1,0],[1,3],[-1,3],[-1,0],[-3,0]],float)


def bounds_for(*polygons):
    points=np.concatenate(polygons);low=points.min(axis=0)-1;high=points.max(axis=0)+1
    return (*low,*high)


def draw_polygon(ctx,p,color=TEAL):
    ctx.line(p,color,width=2,closed=True);ctx.points(p,color,size=5)


def rotation_animation(out,polygon=POLYGON):
    with Context(500,500,title='Continuous rotation — PyOpenGL') as ctx:
        def frame(angle):
            ctx.clear();ctx.panel(0,1,1,(-5,-5,5,5),f'OpenGL | rotation {angle:.0f} degrees');ctx.axes((-5,-5,5,5));draw_polygon(ctx,apply(polygon,rotation(angle)))
        frames=[]
        for angle in range(0,360,10):frame(angle);frames.append(ctx.image())
        save_gif(frames,out/'rotation.gif',70)
        ctx.hold(lambda t:frame((t*60)%360))


def demo(show=False):
    out=output_dir(__file__)
    cases={'Translate (4,2)':translation(4,2),'Rotate 45 degrees':rotation(45),
           'Non-uniform scale (1.6,0.6)':scaling(1.6,.6),'Reflect about y=x':reflection('y=x'),
           'Shear x by 0.8':shear(.8),'Rotate 60 | pivot (2,1)':about(rotation(60),(2,1))}
    data={}
    with Context(title='Lab 3 — 2D transforms / PyOpenGL') as ctx:
        for i,(title,m) in enumerate(cases.items()):
            q=apply(POLYGON,m);data[title]={'matrix':m.tolist(),'vertices':q.tolist()}
            b=bounds_for(POLYGON,q);ctx.panel(i,3,2,b,title);ctx.axes(b);draw_polygon(ctx,POLYGON,GRAY);draw_polygon(ctx,q)
            if 'pivot' in title:ctx.points([(2,1)],(.85,.2,.2),size=7)
        ctx.save(out/'transformations.png');ctx.metadata(out);ctx.hold()
    m=compose(scaling(1.2,.7),shear(.3),rotation(30),translation(3,1));q=apply(COMPLEX,m)
    with Context(700,550,title='Lab 3 — transformed concave polygon') as ctx:
        b=bounds_for(COMPLEX,q);ctx.panel(0,1,1,b,'Concave polygon | scale, shear, rotate, translate');ctx.axes(b);draw_polygon(ctx,COMPLEX,GRAY);draw_polygon(ctx,q);ctx.save(out/'complex_polygon.png');ctx.hold()
    data['complex_polygon']={'matrix':m.tolist(),'vertices':q.tolist()}
    (out/'coordinates.json').write_text(json.dumps(data,indent=2));rotation_animation(out)
    print('Lab 3 OpenGL outputs:',out)


def menu(out=None):
    """Explicit parameter menu; every result is drawn via OpenGL and saved."""
    out=output_dir(__file__) if out is None else out;points=POLYGON.copy()
    with Context(700,600,title='Transformation menu — PyOpenGL') as ctx:
        def display(before,after):
            ctx.clear();b=bounds_for(before,after);ctx.panel(0,1,1,b,'Menu | gray: before / teal: after');ctx.axes(b);draw_polygon(ctx,before,GRAY);draw_polygon(ctx,after);ctx.save(out/'interactive.png');ctx.present()
        display(points,points)
        while True:
            print('\n1 translate | 2 rotate about pivot | 3 scale | 4 reflect | 5 shear | 6 reset | 0 quit')
            try:
                choice=input('Choice: ').strip()
                if choice=='0':break
                if choice=='6':points=POLYGON.copy();display(points,points);continue
                if choice=='1':m=translation(*map(float,input('tx ty: ').split()))
                elif choice=='2':
                    a,x,y=map(float,input('degrees pivot_x pivot_y: ').split());m=about(rotation(a),(x,y))
                elif choice=='3':m=scaling(*map(float,input('sx sy: ').split()))
                elif choice=='4':m=reflection(input('x / y / origin / y=x: ').strip())
                elif choice=='5':m=shear(*map(float,input('shx shy: ').split()))
                else:print('Unknown choice');continue
                new=apply(points,m);display(points,new);points=new
                print('Matrix:\n',m,'\nVertices:\n',points,'\nSaved',out/'interactive.png')
            except (ValueError,TypeError) as e:print('Invalid input:',e)
            except EOFError:break
        ctx.metadata(out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--menu',action='store_true');a=p.parse_args();menu() if a.menu else demo(a.show)
