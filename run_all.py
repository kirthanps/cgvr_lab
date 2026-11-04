"""Run every lab from any working directory and stop on the first failure."""
from pathlib import Path
import subprocess
import sys

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    for lab in range(1,8):
        subprocess.run([sys.executable,'-m',f'lab_{lab:02d}.main'],cwd=root,check=True)
