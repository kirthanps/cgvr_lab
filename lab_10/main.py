"""Lab 10: explicit model/view/projection, homogeneous clipping and viewport mapping."""
import argparse
import csv
import json
import numpy as np
from common.gl_runtime import Context,arguments,output_dir,save_gif
from lab_08.main import ShaderMesh

CUBE=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
EDGES=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]


def unit(v):
    v=np.asarray(v,float)
    if v.shape!=(3,) or not np.isfinite(v).all() or np.linalg.norm(v)<1e-12:raise ValueError('A finite nonzero 3D direction is required')
    return v/np.linalg.norm(v)


def look_at(eye,target,up=(0,1,0)):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    if eye.shape!=(3,) or target.shape!=(3,) or not np.isfinite(eye).all() or not np.isfinite(target).all():raise ValueError('Finite 3D eye and target required')
    forward=unit(target-eye);right=unit(np.cross(forward,unit(up)));vertical=np.cross(right,forward)
    view=np.eye(4);view[:3,:3]=[right,vertical,-forward];view[:3,3]=-view[:3,:3]@eye
    return view


def perspective(fovy,aspect,near,far):
    if not np.isfinite([fovy,aspect,near,far]).all() or not (0<fovy<180 and aspect>0 and 0<near<far):raise ValueError('Require 0<fovy<180, aspect>0 and 0<near<far')
    q=1/np.tan(np.deg2rad(fovy)/2)
    return np.array([[q/aspect,0,0,0],[0,q,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],float)


def orthographic(left,right,bottom,top,near,far):
    if not np.isfinite([left,right,bottom,top,near,far]).all() or not (left<right and bottom<top and 0<near<far):raise ValueError('Invalid orthographic volume')
    return np.array([[2/(right-left),0,0,-(right+left)/(right-left)],[0,2/(top-bottom),0,-(top+bottom)/(top-bottom)],
        [0,0,-2/(far-near),-(far+near)/(far-near)],[0,0,0,1]],float)


def rotation_y(degrees):
    if not np.isfinite(degrees):raise ValueError('Finite rotation required')
    a=np.deg2rad(degrees);c,s=np.cos(a),np.sin(a)
    return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]],float)


def viewport_map(ndc,viewport):
    p=np.asarray(ndc,float);vp=np.asarray(viewport,float)
    if p.shape[-1]!=3 or vp.shape!=(4,) or not np.isfinite(p).all() or not np.isfinite(vp).all() or min(vp[2:])<=0:raise ValueError('Finite NDC xyz and positive viewport width/height required')
    x,y,w,h=vp;return p*np.array([w/2,h/2,.5])+np.array([x+w/2,y+h/2,.5])


def clip_segment(a,b):
    """Clip before division against -w<=x,y,z<=w and guard w>=1e-9."""
    a=np.asarray(a,float);b=np.asarray(b,float)
    if a.shape!=(4,) or b.shape!=(4,) or not np.isfinite([a,b]).all():raise ValueError('Finite homogeneous endpoints required')
    planes=np.array([[1,0,0,1],[-1,0,0,1],[0,1,0,1],[0,-1,0,1],[0,0,1,1],[0,0,-1,1]],float)
    values=list(zip(planes@a,planes@b))+[(a[3]-1e-9,b[3]-1e-9)]
    lo,hi=0.,1.
    for f0,f1 in values:
        if f0<0 and f1<0:return None
        if (f0<0)!=(f1<0):
            t=f0/(f0-f1)
            if f0<0:lo=max(lo,t)
            else:hi=min(hi,t)
            if lo>hi:return None
    d=b-a;return np.array([a+lo*d,a+hi*d])


def stages(vertices,model,view,projection,viewport):
    p=np.asarray(vertices,float)
    if p.ndim!=2 or p.shape[1]!=3 or not np.isfinite(p).all():raise ValueError('Finite Nx3 vertices required')
    matrices=[np.asarray(m,float) for m in (model,view,projection)]
    if any(m.shape!=(4,4) or not np.isfinite(m).all() for m in matrices):raise ValueError('Finite 4x4 matrices required')
    obj=np.column_stack([p,np.ones(len(p))]);world=(matrices[0]@obj.T).T;eye=(matrices[1]@world.T).T;clip=(matrices[2]@eye.T).T
    ndc=np.full((len(p),3),np.nan);screen=np.full((len(p),3),np.nan);safe=clip[:,3]>1e-9
    ndc[safe]=clip[safe,:3]/clip[safe,3,None];screen[safe]=viewport_map(ndc[safe],viewport)
    visible=safe&np.all(np.abs(clip[:,:3])<=clip[:,3,None]+1e-12,axis=1)
    return {'object':obj,'world':world,'eye':eye,'clip':clip,'ndc':ndc,'screen':screen,'visible':visible}


def edge_color(a,b):
    axis=int(np.argmax(np.abs(np.asarray(b)-a)))
    return [( .85,.22,.17),(.07,.47,.57),(.15,.35,.85)][axis]


def cube_data():
    return np.asarray([[*CUBE[i],*edge_color(CUBE[a],CUBE[b])] for a,b in EDGES for i in (a,b)],dtype=np.float32)


def border(ctx,vp):
    g=ctx.gl;x,y,w,h=vp;g.glViewport(0,0,ctx.width,ctx.height);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(0,ctx.width,0,ctx.height,-1,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
    ctx.line([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],(.72,.73,.75),1,closed=True);g.glViewport(*vp)


def cpu_draw(ctx,clip,vp):
    """Explicit clipping/divide/viewport mapping; OpenGL displays the resulting pixels."""
    g=ctx.gl;g.glViewport(0,0,ctx.width,ctx.height);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity();g.glOrtho(0,ctx.width,0,ctx.height,-1,1);g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity()
    for a,b in EDGES:
        line=clip_segment(clip[a],clip[b])
        if line is not None:
            ndc=line[:,:3]/line[:,3,None];screen=viewport_map(ndc,vp);ctx.line(screen[:,:2],edge_color(CUBE[a],CUBE[b]),2)


def save_stage_table(out,data):
    rows=[]
    for i in range(len(CUBE)):
        row={'vertex':i,'inside_clip_volume':bool(data['visible'][i])}
        for name in ('object','world','eye','clip','ndc','screen'):
            for j,value in enumerate(data[name][i]):row[f'{name}_{"xyzw"[j]}']=float(value) if np.isfinite(value) else None
        rows.append(row)
    with (out/'pipeline_coordinates.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)


def demo(eye=(4,3,6),fovy=50,angle=-20):
    out=output_dir(__file__);view=look_at(eye,(0,0,0));model=rotation_y(angle);near,far=.5,30.
    results=[]
    with Context(1440,500,title='Lab 10 — 3D viewing pipeline') as ctx:
        with ShaderMesh(ctx,cube_data(),ctx.gl.GL_LINES) as mesh:
            for i,title in enumerate(['Perspective | MVP in vertex shader','Orthographic | parallel projection','Perspective | smaller viewport']):
                ctx.panel(i,3,1,(-1,-1,1,1),title);vp=ctx.viewport
                if i==2:
                    x,y,w,h=vp;vp=(x+w//5,y+h//5,w*3//5,h*3//5)
                border(ctx,vp);aspect=vp[2]/vp[3]
                proj=orthographic(-2.1*aspect,2.1*aspect,-2.1,2.1,near,far) if i==1 else perspective(fovy,aspect,near,far)
                ctx.gl.glLineWidth(2);mesh.draw(proj@view@model);ctx.gl.glLineWidth(1)
                results.append({'title':title,'viewport':list(vp),'projection':proj.tolist()})
            ctx.save(out/'viewing_pipeline.png');ctx.metadata(out);ctx.hold()
    with Context(1000,500,title='Lab 10 — CPU stages versus OpenGL pipeline') as ctx:
        with ShaderMesh(ctx,cube_data(),ctx.gl.GL_LINES) as mesh:
            for i,title in enumerate(['Explicit CPU clip / divide / viewport','OpenGL clip / divide / viewport']):
                ctx.panel(i,2,1,(-1,-1,1,1),title);vp=ctx.viewport;border(ctx,vp);proj=perspective(fovy,vp[2]/vp[3],near,far)
                data=stages(CUBE,model,view,proj,vp)
                if i==0:
                    cpu_draw(ctx,data['clip'],vp);save_stage_table(out,data)
                    matrices={'model':model.tolist(),'view':view.tolist(),'projection':proj.tolist(),'mvp':(proj@view@model).tolist(),'viewport':list(vp)}
                else:ctx.gl.glLineWidth(2);mesh.draw(proj@view@model);ctx.gl.glLineWidth(1)
            ctx.save(out/'cpu_vs_opengl.png');ctx.hold()
    # Show an edge crossing the near plane and a wholly rejected edge explicitly.
    proj=perspective(60,1,1,10)
    clipping=[]
    for title,a,b in [('Near plane crossing',(-.2,0,-.5),(.5,0,-3)),('Behind camera',(-.3,0,1),(.3,0,2)),('Side plane crossing',(-4,0,-2),(0,0,-2))]:
        line=(proj@np.column_stack([np.array([a,b]),np.ones(2)]).T).T;clipped=clip_segment(*line)
        clipping.append({'case':title,'eye_endpoints':[a,b],'clip_endpoints':line.tolist(),'accepted':clipped is not None,'clipped_endpoints':None if clipped is None else clipped.tolist()})
    with Context(550,500,title='Lab 10 — rotating 3D cube') as ctx:
        with ShaderMesh(ctx,cube_data(),ctx.gl.GL_LINES) as mesh:
            def frame(degrees):
                ctx.clear();ctx.panel(0,1,1,(-1,-1,1,1),f'3D viewing | model rotation {degrees:.0f}');vp=ctx.viewport;border(ctx,vp)
                p=perspective(fovy,vp[2]/vp[3],near,far);ctx.gl.glLineWidth(2);mesh.draw(p@view@rotation_y(degrees));ctx.gl.glLineWidth(1)
            frames=[]
            for degrees in range(0,360,10):frame(degrees);frames.append(ctx.image())
            save_gif(frames,out/'viewing_rotation.gif',70);ctx.hold(lambda t:frame((t*40)%360))
    (out/'results.json').write_text(json.dumps({'convention':'column vectors; right-handed view; eye looks along -Z; OpenGL NDC depth [-1,1]',
        'eye':list(eye),'target':[0,0,0],'fovy':fovy,'near':near,'far':far,'model_rotation_degrees':angle,'matrices':matrices,
        'views':results,'clipping_example_parameters':{'fovy':60,'aspect':1,'near':1,'far':10},'clipping_examples':clipping,'wireframe':'all twelve edges shown; hidden-surface removal is covered separately in Lab 6'},indent=2))
    print('Lab 10 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--eye',nargs=3,type=float,default=[4,3,6]);p.add_argument('--fovy',type=float,default=50);p.add_argument('--angle',type=float,default=-20);a=p.parse_args()
    try:
        look_at(a.eye,(0,0,0));perspective(a.fovy,1,.5,30);rotation_y(a.angle)
    except ValueError as e:p.error(str(e))
    demo(a.eye,a.fovy,a.angle)
