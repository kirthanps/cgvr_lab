"""Lab 4: composite matrices and noncommutative transformation order."""
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from common.transforms import *
from common.display import output_dir,save
from lab_03.main import COMPLEX,draw_polygon,rotation_animation,menu


def demo(show=False):
    out=output_dir(__file__)
    steps=[scaling(1.4,.7),shear(.4),about(rotation(35),(1,1)),reflection('y=x'),translation(5,1)]
    combined=compose(*steps)
    sequential=COMPLEX.copy()
    for m in steps:sequential=apply(sequential,m)
    direct=apply(COMPLEX,combined)
    np.testing.assert_allclose(direct,sequential,atol=1e-12)
    fig,axes=plt.subplots(1,3,figsize=(14,5))
    for ax,title,mat in [(axes[0],'Scale → shear → pivot rotate → reflect → translate',combined),
                         (axes[1],'Rotate 45 → translate (5, 0)',compose(rotation(45),translation(5,0))),
                         (axes[2],'Translate (5, 0) → rotate 45',compose(translation(5,0),rotation(45)))]:
        draw_polygon(ax,COMPLEX,'Original','#888888');draw_polygon(ax,apply(COMPLEX,mat),'Result','#147d92');ax.set_title(title,fontsize=10);ax.legend(fontsize=8)
    save(fig,out/'composition.png',show)
    fig,axes=plt.subplots(1,4,figsize=(14,4));current=COMPLEX.copy()
    for ax,(title,m) in zip(axes,[('Scale',scaling(1.5,.6)),('Reflect y=x',reflection('y=x')),('Pivot rotation',about(rotation(30),(1,1))),('Translate',translation(4,1))]):
        previous=current;current=apply(current,m);draw_polygon(ax,previous,'Before','#999999');draw_polygon(ax,current,'After','#147d92');ax.set_title(title);ax.legend(fontsize=8)
    save(fig,out/'stages.png')
    rotation_animation(out,COMPLEX)
    (out/'matrices.json').write_text(json.dumps({'convention':'column vectors; matrices listed in application order',
        'steps':[m.tolist() for m in steps],'combined':combined.tolist(),'vertices':direct.tolist(),
        'maximum_sequential_error':float(np.max(np.abs(direct-sequential)))},indent=2))
    print('Lab 4 outputs:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--show',action='store_true');p.add_argument('--menu',action='store_true');a=p.parse_args();menu() if a.menu else demo(a.show)
