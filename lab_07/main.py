"""Lab 7: per-surface-point Phong illumination on an analytic 3D sphere."""
import argparse
import json
import numpy as np
from PIL import Image
from common.gl_runtime import Context,output_dir,arguments


def normalize(v):
    v=np.asarray(v,float);length=np.linalg.norm(v,axis=-1,keepdims=True)
    if np.any(length<1e-12):raise ValueError('Cannot normalize zero-length vector')
    return v/length


def phong(points,normals,light=(3,4,5),eye=(0,0,5),ka=.12,kd=.65,ks=.5,shininess=32,base=(.12,.48,.72)):
    """Return unclamped ambient, diffuse and specular RGB for point arrays (...,3)."""
    if min(ka,kd,ks)<0 or shininess<=0:raise ValueError('Nonnegative coefficients and positive shininess required')
    points=np.asarray(points,float);normals=np.asarray(normals,float);base=np.asarray(base,float)
    light=np.asarray(light,float);eye=np.asarray(eye,float)
    if points.shape!=normals.shape or points.shape[-1]!=3 or base.shape!=(3,) or light.shape!=(3,) or eye.shape!=(3,):raise ValueError('Expected matching 3D points/normals and 3D light, eye, base')
    if not all(np.isfinite(a).all() for a in (points,normals,base,light,eye)) or not np.isfinite([ka,kd,ks,shininess]).all():raise ValueError('Finite inputs required')
    n=normalize(normals);l=normalize(light-points);v=normalize(eye-points)
    ndotl=np.sum(n*l,axis=-1,keepdims=True)
    r=2*ndotl*n-l
    # Light behind the surface contributes neither diffuse nor specular illumination.
    spec=np.where(ndotl>0,np.maximum(np.sum(r*v,axis=-1,keepdims=True),0)**shininess,0)
    ambient=np.broadcast_to(ka*base,points.shape).copy()
    diffuse=kd*base*np.maximum(ndotl,0)
    specular=ks*np.ones(3)*spec
    return ambient,diffuse,specular


def sphere(size=320,**kwargs):
    axis=np.linspace(-1.12,1.12,size);x,y=np.meshgrid(axis,axis)
    mask=x*x+y*y<=1;z=np.sqrt(np.maximum(0,1-x*x-y*y))
    points=np.stack([x[mask],y[mask],z[mask]],axis=-1)
    parts=phong(points,points,**kwargs)
    images=[]
    for colors in (*parts,sum(parts)):
        image=np.full((size,size,3),.96);image[mask]=np.clip(colors,0,1);images.append(image)
    return images,mask


def compile_phong(ctx):
    from pathlib import Path
    from OpenGL.GL.shaders import compileProgram,compileShader
    g=ctx.gl;root=Path(__file__).resolve().parent/'shaders'
    return compileProgram(compileShader((root/'phong.vert').read_text(),g.GL_VERTEX_SHADER),
                          compileShader((root/'phong.frag').read_text(),g.GL_FRAGMENT_SHADER))


def uniforms(ctx,program,light=(3,4,5),shininess=32,component=3,base=(.12,.48,.72),ka=.12,kd=.65,ks=.5):
    g=ctx.gl
    for name,value in [('lightPosition',light),('eyePosition',(0,0,5)),('baseColor',base)]:g.glUniform3f(g.glGetUniformLocation(program,name),*value)
    for name,value in [('ka',ka),('kd',kd),('ks',ks),('shininess',shininess)]:g.glUniform1f(g.glGetUniformLocation(program,name),float(value))
    g.glUniform1i(g.glGetUniformLocation(program,'component'),component)


def sphere_mesh(stacks=40,slices=80):
    """Triangle mesh with analytic unit-sphere vertex normals (position = normal)."""
    def point(i,j):
        theta=np.pi*i/stacks;phi=2*np.pi*j/slices
        return (np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta))
    vertices=[]
    for i in range(stacks):
        for j in range(slices):
            a,b,c,d=point(i,j),point(i+1,j),point(i+1,j+1),point(i,j+1)
            if i>0:vertices.extend((a,b,d))
            if i<stacks-1:vertices.extend((b,c,d))
    return np.asarray(vertices,dtype=np.float32)


def draw_sphere(ctx,program,mesh,light=(3,4,5),shininess=32,component=3):
    g=ctx.gl;g.glClear(g.GL_DEPTH_BUFFER_BIT);g.glEnable(g.GL_DEPTH_TEST);g.glDepthFunc(g.GL_LESS);g.glUseProgram(program)
    uniforms(ctx,program,light,shininess,component)
    # Vertex arrays submit real triangle geometry and normals to the shader pipeline.
    g.glEnableClientState(g.GL_VERTEX_ARRAY);g.glEnableClientState(g.GL_NORMAL_ARRAY)
    g.glVertexPointer(3,g.GL_FLOAT,0,mesh);g.glNormalPointer(g.GL_FLOAT,0,mesh)
    g.glDrawArrays(g.GL_TRIANGLES,0,len(mesh))
    g.glDisableClientState(g.GL_VERTEX_ARRAY);g.glDisableClientState(g.GL_NORMAL_ARRAY)
    g.glUseProgram(0);g.glDisable(g.GL_DEPTH_TEST);ctx.check()


def render_comparison(out,name,titles,settings,mesh):
    with Context(400*len(titles),430,title='Lab 7 — Phong GLSL / PyOpenGL') as ctx:
        program=compile_phong(ctx)
        try:
            for i,(title,params) in enumerate(zip(titles,settings)):
                ctx.panel(i,len(titles),1,(-1.12,-1.12,1.12,1.12),title);draw_sphere(ctx,program,mesh,**params)
            ctx.save(out/name);ctx.metadata(out);ctx.hold()
        finally:ctx.gl.glDeleteProgram(program)


def demo(light=(3,4,5),shininess=32,show=False):
    # Validate the same model parameters before creating a context.
    phong([[0,0,1]],[[0,0,1]],light=light,shininess=shininess)
    out=output_dir(__file__);mesh=sphere_mesh()
    render_comparison(out,'phong_components.png',['Ambient','Diffuse | Lambert','Specular | Phong','Combined | GLSL fragments'],
        [dict(light=light,shininess=shininess,component=i) for i in range(4)],mesh)
    render_comparison(out,'shininess.png',[f'Shininess {n}' for n in (8,32,128)],
        [dict(light=light,shininess=n) for n in (8,32,128)],mesh)
    positions=[(-3,4,5),(3,4,5),(0,-4,3)]
    render_comparison(out,'light_positions.png',[f'Light {pos}' for pos in positions],
        [dict(light=pos,shininess=shininess) for pos in positions],mesh)
    with Context(500,500,title='Lab 7 — live shader-rendered sphere') as ctx:
        program=compile_phong(ctx)
        try:
            def frame(angle=0):
                ctx.clear();ctx.panel(0,1,1,(-1.12,-1.12,1.12,1.12),'Phong illumination | real GLSL')
                pos=light if angle==0 else (4*np.cos(angle),4*np.sin(angle),5)
                draw_sphere(ctx,program,mesh,light=pos,shininess=shininess)
            frame();ctx.save(out/'phong_sphere.png');ctx.hold(lambda t:frame(t*.6+.001))
        finally:ctx.gl.glDeleteProgram(program)
    a,d,s=phong(np.array([[0.,0.,1.]]),np.array([[0.,0.,1.]]),light=light,shininess=shininess)
    (out/'results.json').write_text(json.dumps({'object':'unit sphere triangle mesh; 40 stacks x 80 slices','triangles':len(mesh)//3,
        'lighting':'per-fragment GLSL reflection-vector Phong','eye':[0,0,5],'light':list(light),'ka':.12,'kd':.65,'ks':.5,'shininess':shininess,'base_rgb':[.12,.48,.72],
        'cpu_reference_front_pole':{'ambient':a[0].tolist(),'diffuse':d[0].tolist(),'specular':s[0].tolist(),'combined_unclamped':(a+d+s)[0].tolist()}},indent=2))
    print('Lab 7 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--light',type=float,nargs=3,default=[3,4,5]);p.add_argument('--shininess',type=float,default=32);a=p.parse_args()
    try:demo(a.light,a.shininess,a.show)
    except ValueError as e:p.error(str(e))
