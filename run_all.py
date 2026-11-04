"""Run all seven real OpenGL lab demonstrations from any working directory."""
import argparse
from pathlib import Path
import subprocess
import sys

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--headless',action='store_true',help='Linux EGL export without opening windows');a=p.parse_args()
    root=Path(__file__).resolve().parent
    for lab in range(1,8):
        command=[sys.executable,'-m',f'lab_{lab:02d}.main']
        if a.headless:command.append('--headless')
        subprocess.run(command,cwd=root,check=True)
