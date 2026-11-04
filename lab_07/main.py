"""Lab 7: per-surface-point Phong illumination on an analytic 3D sphere."""
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from common.display import output_dir,save


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


def demo(light=(3,4,5),shininess=32,show=False):
    out=output_dir(__file__);images,mask=sphere(light=light,shininess=shininess)
    fig,axes=plt.subplots(1,4,figsize=(14,4))
    for ax,img,title in zip(axes,images,['Ambient','Diffuse (Lambert)','Specular (Phong)','Combined illumination']):
        ax.imshow(img,origin='lower');ax.axis('off');ax.set_title(title)
    save(fig,out/'phong_components.png',show)
    Image.fromarray((np.flipud(images[-1])*255).astype('uint8')).save(out/'phong_sphere.png')
    fig,axes=plt.subplots(1,3,figsize=(11,4))
    for ax,n in zip(axes,[8,32,128]):
        img,_=sphere(light=light,shininess=n);ax.imshow(img[-1],origin='lower');ax.axis('off');ax.set_title(f'Shininess {n}')
    save(fig,out/'shininess.png')
    fig,axes=plt.subplots(1,3,figsize=(11,4))
    for ax,pos in zip(axes,[(-3,4,5),(3,4,5),(0,-4,3)]):
        img,_=sphere(light=pos,shininess=shininess);ax.imshow(img[-1],origin='lower');ax.axis('off');ax.set_title(f'Light {pos}')
    save(fig,out/'light_positions.png')
    a,d,s=phong(np.array([[0.,0.,1.]]),np.array([[0.,0.,1.]]),light=light,shininess=shininess)
    (out/'results.json').write_text(json.dumps({'object':'unit sphere centered at origin','eye':[0,0,5],'light':list(light),
        'ka':.12,'kd':.65,'ks':.5,'shininess':shininess,'base_rgb':[.12,.48,.72],
        'visible_surface_samples':int(mask.sum()),'front_pole':{'point':[0,0,1],'ambient':a[0].tolist(),'diffuse':d[0].tolist(),'specular':s[0].tolist(),'combined_unclamped':(a+d+s)[0].tolist()}},indent=2))
    print('Lab 7 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--light',type=float,nargs=3,default=[3,4,5]);p.add_argument('--shininess',type=float,default=32);p.add_argument('--show',action='store_true');a=p.parse_args()
    try:demo(a.light,a.shininess,a.show)
    except ValueError as e:p.error(str(e))
