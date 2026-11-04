# Validation record

Verified with Python 3.12.14, NumPy 2.3.5, Matplotlib 3.10.8 and Pillow 13.0.0.

## Executed checks

- `python run_all.py`: executes Labs 1–7 sequentially; generated output is logged in `execution.txt`.
- `python -m unittest discover -s tests -v`: 18 tests passed; exact output is in `validation.txt`.
- `python validate_outputs.py`: confirmed 19 images/animations and 145 decoded frames; fully decodes every PNG/GIF frame, loads JSON and NumPy results, rejects empty output files, and checks local Markdown file links.
- Interactive transformation menu: a scripted session exercised translation, pivot rotation, scaling, reflection, shear, reset and exit. Transcript: `lab_03/outputs/menu_session.txt`; resulting image: `lab_03/outputs/interactive.png`.
- Visual inspection of the seven primary result figures and an animation contact sheet checked the actual generated outputs.

## What the tests establish

| Lab | Evidence |
|---|---|
| 1 | All endpoints in a 17×17 grid; endpoint inclusion, dominant-axis count, connected pixels, bounded line error, styles, and zero-length line |
| 2 | Circle radii 0–40, rotational symmetry, distance error, ellipse symmetry, degenerate axes, invalid radius, and fractional antialias coverage |
| 3 | Independently known transform coordinates, pivot invariance, inverse round trip, rotation determinant and nonfinite input rejection |
| 4 | Composite versus sequential application on 50 seeded points; known order-dependent results |
| 5 | Special cases and 1,000 seeded random segments checked against a separate parametric-interval clipping oracle |
| 6 | Known interpolated depth, nearest-color selection, background infinity, reversed submission order, opposite winding, degenerate triangles and equal-depth tie policy |
| 7 | Analytic aligned-light RGB values, back-facing light suppression, normal normalization, shininess response and finite rendered sphere samples |

These checks verify the delivered demonstrations and covered edge cases; they do not claim exhaustive verification for arbitrary numerical magnitudes, GPU rendering, or every desktop image viewer. No Unity work or GitHub publishing was performed.
