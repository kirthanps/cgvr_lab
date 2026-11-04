"""Display computed pixels; graphics algorithms live in each lab, not in plotting calls."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def output_dir(module_file):
    path = Path(module_file).resolve().parent / 'outputs'
    path.mkdir(exist_ok=True)
    return path


def pixels(ax, points, title, color='#147d92'):
    points = np.asarray(list(points))
    if len(points):
        ax.scatter(points[:, 0], points[:, 1], s=9, marker='s', c=color, linewidths=0)
    ax.set(title=title, xlabel='x (pixels)', ylabel='y (pixels)', aspect='equal')
    ax.grid(alpha=.2)


def save(fig, path, show=False):
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor='white')
    if show:
        # Open the saved image via the local desktop; headless execution needs no GUI.
        from PIL import Image
        Image.open(path).show()
    plt.close(fig)
