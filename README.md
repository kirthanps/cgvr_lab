# CS4104 — Computer Graphics and Virtual Reality: Labs 1–7

Python implementations based on the **RV University CG & VR Lab Manual, academic year 2026–27**. This repository contains algorithm source, runnable examples, generated PNG/GIF outputs, numerical results, measured benchmarks, tests, assignment mappings, and viva answers. Python was explicitly approved by the requester. Labs 8–10 are outside this deliverable.

## Setup and run

Python 3.12 was used for verification. From the repository root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell alternative:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_all.py
python -m unittest discover -s tests -v
python validate_outputs.py
```

No Unity or OpenGL installation is needed for these Python implementations. The algorithms calculate pixels, matrices, depth, and lighting explicitly; NumPy provides array arithmetic, Matplotlib displays results, and Pillow writes raster animations. This is a software-rendered adaptation, not a PyOpenGL port. It runs headlessly and saves results into each lab's `outputs/` folder. Add `--show` to an individual lab command to open its saved demonstration image with the desktop image viewer. On a headless machine, open the PNG/GIF files yourself.

## Lab index

| Lab | Topic | Run from the root | Documentation |
|---|---|---|---|
| 1 | DDA and Bresenham | `python -m lab_01.main` | [Lab 1](lab_01/README.md) |
| 2 | Midpoint circle and ellipse | `python -m lab_02.main` | [Lab 2](lab_02/README.md) |
| 3 | 2D homogeneous transformations | `python -m lab_03.main` | [Lab 3](lab_03/README.md) |
| 4 | Composite transformations | `python -m lab_04.main` | [Lab 4](lab_04/README.md) |
| 5 | Cohen–Sutherland clipping | `python -m lab_05.main` | [Lab 5](lab_05/README.md) |
| 6 | Z-buffer hidden-surface removal | `python -m lab_06.main` | [Lab 6](lab_06/README.md) |
| 7 | Phong illumination on a 3D sphere | `python -m lab_07.main` | [Lab 7](lab_07/README.md) |

For interaction, run `python -m lab_03.main --menu` or `python -m lab_04.main --menu`. All lab modules support `--help`. Import algorithm functions for custom inputs; the README examples and tests show the interfaces.

## Coverage and manual inconsistencies

Labs 1 and 2 include all eight assignment extensions. Labs 3 and 4 cover the full transformation assignment set. The manual repeats transformation aims, questions, and assignments under Labs 5–7 despite their different titles. As confirmed by the requester, this repository implements each titled algorithm **and** maps every repeated question to the completed transformation work. Each affected README preserves its manual question numbering. The duplicated `y=xy=xy=x` wording is read as reflection about **y=x**.

Coordinate conventions and limitations are documented per lab. All PNG/GIF files are actual program-generated outputs, not fabricated screenshots. Numerical outputs are available as JSON, CSV, or NumPy arrays. Timing numbers describe this execution environment and may change when rerun. No Word or PDF reports are created; the source manual is not bundled.

## Validation

See [VALIDATION.md](VALIDATION.md) for executed checks and [validation.txt](validation.txt) for test output. Tests cover octants, degenerate geometry, circle symmetry, matrix invariants, an independent clipping oracle, interpolated depths, submission-order behavior, and analytic Phong values.

## Local Git repository

The supplied ZIP includes `.git/` and a `main` branch with the completed files committed. After extraction:

```bash
git status
git log --oneline
```

The repository is ready to upload to GitHub. It has no remote configured and has not been published to a GitHub account. To publish, create an empty GitHub repository, then run `git remote add origin YOUR_REPOSITORY_URL` and `git push -u origin main`. Choose the repository visibility yourself.
