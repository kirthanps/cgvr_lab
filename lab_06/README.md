# Lab 6 — Z-buffer hidden-surface removal in OpenGL

Run `python -m lab_06.main` for the real OpenGL window. Close it or press Escape to exit. Use `--headless` on Linux with Mesa/EGL to export without a display server.

The demonstration submits 3D triangles using PyOpenGL. OpenGL rasterizes them, interpolates depth, and resolves visibility with `GL_DEPTH_TEST` and `glDepthFunc(GL_LESS)`. The depth buffer clears to 1.0. Orthographic projection uses eye-space z = -input_depth, so a smaller input depth means a nearer surface. The first panel disables depth testing; the second enables it. The third visualizes the actual `GL_DEPTH_COMPONENT` readback (blue near, red far).

![Visibility and depth](outputs/visibility.png)

## Explicit implementation and independent comparison

`render` retains the explicit Python/NumPy Z-buffer implementation: test pixel-center triangle coverage, interpolate z barycentrically, compare, and update color/depth/owner. `draw_triangles` is the separate OpenGL path. The program compares CPU depths with actual GL depths on common covered pixels, then reverses submission order and checks the OpenGL result again.

`outputs/depth.npy` is the actual OpenGL depth readback (1.0 means untouched); `depth_reference.npy` is the explicit CPU result (infinity means untouched). Both use bottom-left array indexing `[y,x]`. `object_ids.npy` is the CPU reference's triangle index buffer. `zbuffer_color.png` is the real GL color buffer, flipped only for top-left image encoding. `results.json` reports measured coverage differences, maximum depth discrepancy, and a probe pixel. `opengl.json` records vendor, version, backend and actual depth precision.

Equal depths retain the first surface. OpenGL uses its normal polygon edge fill rules; the CPU reference uses inclusive edges, so boundary coverage can differ on other geometry. This example uses opaque orthographic triangles; transparency, perspective-correct attributes, and Z-fighting avoidance are outside its scope. CPU storage is O(width×height), and work scales with summed triangle bounding-box areas.

## Repeated manual questions

The repeated transformation assignments 25–32 and viva 46–60 are included through these mappings.

| Assignment | Completed exercise |
|---|---|
| 25. Pivot rotation | [Lab 3](../lab_03/README.md), assignment 1 |
| 26. Non-uniform scale | Lab 3, assignment 2 |
| 27. Reflection y=x | Lab 3, assignment 3 |
| 28. Menu | `python -m lab_03.main --menu` |
| 29. Rotation animation | [GIF](../lab_03/outputs/rotation.gif) |
| 30. 2D/3D comparison | Lab 3 comparison table |
| 31. Matrix multiplication | `common/transforms.py:apply` |
| 32. Complex polygon | [Lab 4](../lab_04/README.md) |

For viva 46–60 subtract 45 to find the corresponding [Lab 3 answer](../lab_03/README.md#viva-answers-manual-115).

## Topic-specific viva preparation

- Hidden-surface removal selects the nearest visible surface at each sample.
- A Z-buffer stores depth separately from color.
- It resolves intersecting faces without a global polygon sort.
- Z-fighting arises from limited depth precision or nearly coplanar surfaces.
- Transparency requires more than the nearest opaque surface.
