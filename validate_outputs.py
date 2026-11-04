"""Verify generated artifacts are complete and README file targets resolve."""
from pathlib import Path
import json
import re
from PIL import Image
import numpy as np


def validate(root):
    count=frames=0
    for path in sorted(root.glob('lab_*/outputs/*')):
        if path.stat().st_size==0:raise ValueError(f'Empty output: {path}')
        if path.suffix in ('.png','.gif'):
            with Image.open(path) as im:
                for index in range(getattr(im,'n_frames',1)):
                    im.seek(index);im.load();frames+=1
            count+=1
        elif path.suffix=='.json':json.loads(path.read_text())
        elif path.suffix=='.npy':np.load(path,allow_pickle=False)
    for readme in root.rglob('*.md'):
        for dest in re.findall(r'\]\(([^)]+)\)',readme.read_text()):
            dest=dest.split('#')[0]
            if dest and '://' not in dest and not (readme.parent/dest).exists():
                raise ValueError(f'Broken local link: {readme}: {dest}')
    print(f'Validated {count} images/animations, {frames} decoded frames, numerical outputs, and local Markdown file links.')


if __name__=='__main__':validate(Path(__file__).resolve().parent)
