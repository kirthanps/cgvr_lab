# CS4104 — Computer Graphics and Virtual Reality: Labs 1–7 with PyOpenGL

**This revision uses real OpenGL in Python for every lab.** PyOpenGL submits points, lines, and triangles to OpenGL; GLFW creates desktop windows. Lab 6 uses an actual depth buffer, and Lab 7 compiles GLSL vertex and fragment shaders for per-fragment Phong illumination. There is no Matplotlib dependency or plotting-based scene rendering.

Based on the RV University CG & VR Lab Manual, academic year 2026–27. The repository includes a main README, seven lab folders, source, actual framebuffer captures, animations, measurements, assignment mappings, viva answers, and automated checks. Labs 8–10 remain outside this deliverable.

## Install

Use Python 3.12 (the tested version) and an OpenGL-capable desktop driver:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The code uses **OpenGL 2.1 compatibility APIs and GLSL 1.20**, which keeps the point-generation and transformation exercises easy to inspect. It does not require a core-profile context. GLFW's wheel supplies its native library on supported platforms; the operating system still needs an OpenGL driver and the usual window-system libraries. No GLUT, Unity, or C++ compiler is required for these seven labs.

## Run on your desktop

```bash
python -m lab_01.main
python -m lab_02.main --center 15 -10 --radius 35
python -m lab_03.main
python -m lab_03.main --menu
python -m lab_04.main
python -m lab_05.main
python -m lab_06.main
python -m lab_07.main --light -3 4 5 --shininess 64
```

Each default demo opens one or more **OpenGL windows**. Close the current window or press Escape to continue to the next view. The animation windows update continuously. All generated PNGs, GIFs, JSON/CSV, and arrays go to the corresponding `outputs/` folder. The transformation menu accepts parameters in the terminal and redraws its OpenGL window after each choice; keep the terminal focused while entering values. Lab 4's menu saves into Lab 4's folder.

Run `python run_all.py` for the seven demos sequentially. It waits while each desktop window is open. All lab modules support `--help`; the retained `--show` flag is unnecessary because desktop windows open by default.

## Linux headless export and actual verification

A display server is unnecessary when using the included **EGL pbuffer** backend with a Mesa/EGL desktop OpenGL installation:

```bash
python run_all.py --headless
python -m lab_07.main --headless
python -m unittest discover -s tests -v
CG_HEADLESS=1 CG_GL_TEST=1 python -m unittest discover -s tests -v
python validate_outputs.py
```

`--headless` is Linux/EGL mode; use ordinary desktop mode on Windows/macOS. It still creates a real OpenGL context and runs the same OpenGL calls and shaders. It does not select an image-library replacement. If EGL is unavailable on a Linux machine, install the distribution's Mesa EGL/OpenGL packages or use desktop mode.

The supplied captures were generated with **Mesa llvmpipe, OpenGL 4.5 compatibility, GLSL 4.50, and a 24-bit depth buffer**, through EGL. llvmpipe implements OpenGL on the CPU; no physical GPU acceleration is claimed. GLFW desktop display/event handling could not be exercised in this headless environment. Actual OpenGL geometry, depth testing, shader compilation, shader output, framebuffer readback, and EGL context lifecycle were exercised successfully.

## Lab index and coverage

| Lab | Topic and actual OpenGL use | Documentation |
|---|---|---|
| 1 | Explicit DDA/Bresenham pixels submitted with `GL_POINTS` | [Lab 1](lab_01/README.md) |
| 2 | Midpoint circles/ellipses as GL points; GL smoothing and supersampled GL readback | [Lab 2](lab_02/README.md) |
| 3 | Homogeneous transformed vertices as GL outlines/points; animated redraws | [Lab 3](lab_03/README.md) |
| 4 | Composite transforms and order comparisons drawn in OpenGL | [Lab 4](lab_04/README.md) |
| 5 | Explicit Cohen–Sutherland clipping, then GL line rendering | [Lab 5](lab_05/README.md) |
| 6 | Triangle geometry with `GL_DEPTH_TEST` / `GL_LESS`; actual color/depth readback | [Lab 6](lab_06/README.md) |
| 7 | Triangle sphere mesh, vertex normals, GLSL vertex/fragment Phong lighting | [Lab 7](lab_07/README.md) |

Labs 1–2 include all eight assignment extensions. Labs 3–4 include the complete transformation assignment set. The manual repeats transformation material under Labs 5–7; as requested, those folders implement the titled algorithms **and** explicitly map every repeated assignment/viva question to the completed transformation exercises. The malformed `y=xy=xy=x` text is interpreted as reflection in **y=x**.

## Rendering evidence

Every scene image and every animation frame originates in `glReadPixels` after OpenGL rendering. Pillow encodes the captures, supplies text glyphs uploaded to OpenGL, and area-averages the high-resolution GL circle for supersampling. It does not draw the lab geometry. NumPy performs explicit algorithm and matrix arithmetic. The CPU Z-buffer and analytic Phong functions are retained as independent references and tests; the delivered Lab 6/7 scene captures use OpenGL geometry and depth/shader processing.

Each lab includes `outputs/opengl.json` with the actual vendor, renderer, version, backend, framebuffer size, and depth bits. [VALIDATION.md](VALIDATION.md) explains the tests and measured limits. [validation.txt](validation.txt) contains the executed test log; [execution.txt](execution.txt) records the full headless run. No Word or PDF reports are included.

## Git repository

The ZIP includes `.git/`, the `main` branch, and the prior revision followed by the OpenGL conversion commit. After extraction, `git status` should be clean and `git log --oneline` shows both revisions. The repository has no remote and has not been published to a GitHub account. To publish it, create an empty repository on GitHub, choose its visibility, then run:

```bash
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## Primary API references

- [PyOpenGL documentation](https://pyopengl.sourceforge.net/)
- [GLFW context creation](https://www.glfw.org/docs/latest/context_guide.html)
- [OpenGL depth testing](https://wikis.khronos.org/opengl/Depth_Test)
- [OpenGL framebuffer readback](https://pyopengl.sourceforge.net/documentation/manual-3.0/glReadPixels.html)
- [Khronos OpenGL specifications and GLSL](https://registry.khronos.org/OpenGL/)
