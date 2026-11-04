# Validation — PyOpenGL revision

## Executed environment

Python 3.12.14, PyOpenGL 3.1.10, GLFW Python package 2.10.0, NumPy 2.3.5, Pillow 13.0.0. Actual GL contexts used Linux EGL pbuffer surfaces, Mesa llvmpipe, OpenGL 4.5 compatibility, GLSL 4.50, and 24-bit depth. This is actual OpenGL execution through Mesa's CPU driver, not a physical GPU test. The implementation targets compatibility OpenGL 2.1 / GLSL 1.20; that minimum-version driver and GLFW desktop windows were not independently exercised here.

## Commands and results

- `python run_all.py --headless`: all seven labs rendered using OpenGL. The log is in `execution.txt`.
- `CG_HEADLESS=1 CG_GL_TEST=1 python -m unittest discover -s tests -v`: **21 tests passed**, including all three actual OpenGL integration tests. The log is in `validation.txt`.
- `python validate_outputs.py`: validated **20 image/animation files and 146 decoded frames**; decodes PNG/GIF frames, loads JSON/NumPy data, rejects empty outputs, checks local Markdown links, and verifies OpenGL context metadata for all seven labs.
- Both transformation menus were exercised with scripted parameters in headless OpenGL mode. Transcripts and framebuffer captures are in the respective Lab 3/4 outputs folders.
- All seven primary figures, the shader comparisons, and animation frame contact sheets were visually reviewed.

Ordinary unit-test discovery intentionally skips the three context-dependent tests unless `CG_GL_TEST=1` is set. The delivered execution log used that flag and contains no skips. `CG_HEADLESS=1` selects EGL before OpenGL imports.

## Algorithm and rendering checks

| Lab | Executed evidence |
|---|---|
| 1 | Integer endpoints across a 17×17 grid, all octants, connected pixels, bounded line error, style/brush cases, zero-length lines; a real GL point readback test checks generated line samples |
| 2 | Radii 0–40, circle symmetry and distance error, ellipse symmetry, degenerate axes, invalid radius and fractional antialias coverage; actual circle/ellipse/ring GL exports |
| 3 | Known transform coordinates, pivot invariance, inverse round trips, rotation determinant, nonfinite rejection; OpenGL matrix results and parameter menu exports |
| 4 | Composite versus sequential application on 50 seeded points and independently known noncommutative results; GL comparisons and menu export |
| 5 | Special cases and 1,000 random segments compared with a separate parametric interval clipping oracle; clipped segments drawn in OpenGL |
| 6 | CPU depth interpolation, nearest surface, winding, degenerate geometry, tie policy; independent actual GL depth readback, reversed submission order and CPU/GL comparison |
| 7 | CPU analytic lighting values, back-light suppression, normalization and shininess; actual vertex/fragment shader compilation/linking, sphere mesh draws, and a rendered planar shader sample compared with a known RGB result |

The Lab 6 demo measured maximum common-pixel CPU/GL depth discrepancy of approximately **1.01×10⁻⁷**, with identical coverage for the included scene. Results and probe coordinates are preserved in `lab_06/outputs/results.json`; different meshes may differ at polygon edges because OpenGL and the inclusive CPU reference use different fill rules.

The GLSL integration test compares a framebuffer sample against the analytic ambient + diffuse + specular sum, allowing one 8-bit color quantization step. GL error checks run after framebuffer reads and shader draws. PNGs and GIFs are real GL readbacks; the supersampled circle is downsampled from a GL framebuffer.

These checks establish the delivered demos and tested cases. They do not establish arbitrary desktop-driver compatibility, exhaustive numerical correctness, perspective/transparency behavior, or physical illumination accuracy. No Unity work or GitHub publication was performed.
