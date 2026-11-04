"""Lab 4: composite matrices and transformation order rendered through OpenGL."""
import argparse
import json
import numpy as np
from common.transforms import *
from common.gl_runtime import Context,output_dir,arguments,GRAY
from lab_03.main import COMPLEX,draw_polygon,rotation_animation,menu,bounds_for


def demo(show=False):
    out=output_dir(__file__)
    steps=[scaling(1.4,.7),shear(.4),about(rotation(35),(1,1)),reflection('y=x'),translation(5,1)]
    combined=compose(*steps);sequential=COMPLEX.copy()
    for m in steps:sequential=apply(sequential,m)
    direct=apply(COMPLEX,combined);np.testing.assert_allclose(direct,sequential,atol=1e-12)
    cases=[('Scale, shear, pivot rotate, reflect, translate',combined),
           ('Rotate 45 -> translate (5,0)',compose(rotation(45),translation(5,0))),
           ('Translate (5,0) -> rotate 45',compose(translation(5,0),rotation(45)))]
    with Context(1440,500,title='Lab 4 — composite transformations / PyOpenGL') as ctx:
        for i,(title,m) in enumerate(cases):
            q=apply(COMPLEX,m);b=bounds_for(COMPLEX,q);ctx.panel(i,3,1,b,title);ctx.axes(b);draw_polygon(ctx,COMPLEX,GRAY);draw_polygon(ctx,q)
        ctx.save(out/'composition.png');ctx.metadata(out);ctx.hold()
    with Context(1440,420,title='Lab 4 — intermediate OpenGL geometry') as ctx:
        current=COMPLEX.copy()
        for i,(title,m) in enumerate([('Scale',scaling(1.5,.6)),('Reflect y=x',reflection('y=x')),('Pivot rotation',about(rotation(30),(1,1))),('Translate',translation(4,1))]):
            before=current;current=apply(current,m);b=bounds_for(before,current);ctx.panel(i,4,1,b,title);ctx.axes(b);draw_polygon(ctx,before,GRAY);draw_polygon(ctx,current)
        ctx.save(out/'stages.png');ctx.hold()
    rotation_animation(out,COMPLEX)
    (out/'matrices.json').write_text(json.dumps({'convention':'column vectors; matrices listed in application order','steps':[m.tolist() for m in steps],
        'combined':combined.tolist(),'vertices':direct.tolist(),'maximum_sequential_error':float(np.max(np.abs(direct-sequential)))},indent=2))
    print('Lab 4 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--menu',action='store_true');a=p.parse_args();menu(output_dir(__file__)) if a.menu else demo(a.show)
