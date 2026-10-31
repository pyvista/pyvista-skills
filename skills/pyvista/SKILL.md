---
name: pyvista
description: Write, debug, and review Python code that uses PyVista for 3D visualization, mesh processing, and VTK datasets. Use whenever a task creates, changes, tests, or reviews code importing pyvista, builds or inspects meshes (PolyData, UnstructuredGrid, ImageData, StructuredGrid), renders 3D scenes, or converts matplotlib/2D plotting tasks into 3D visualization. Do not use for matplotlib, general NumPy-only work, or VTK C++ pipelines that do not touch the pyvista API.
---

# PyVista

Write the smallest PyVista code that renders the requested result correctly. PyVista is the Pythonic VTK layer: meshes are NumPy-backed objects, filters return new meshes, and rendering goes through `Plotter`.

## Imports and versions

```python
import numpy as np
import pyvista as pv
```

- Check `pv.vtk_version_info()` when behavior differs across VTK. Assume VTK >= 9 and PyVista >= 0.43 unless the project pins otherwise.
- Never import `vtk` directly when `pv` covers the operation. Drop to `vtk` only for features PyVista does not wrap, and say why in a comment.

## Core workflow

```python
mesh = pv.Sphere()                 # any PolyData/UnstructuredGrid/...
pl = pv.Plotter()
pl.add_mesh(mesh, color="tan", show_edges=True)
pl.show()
```

1. Build or load the dataset.
2. Create one `Plotter`, add actors with `add_mesh`.
3. Call `pl.show()` (interactive) or `pl.screenshot(path)` (headless).

`pl.show()` finalizes the plotter. Do not add meshes after it. Open a new `Plotter` for the next figure instead of reusing one.

## Datasets

| Class                 | Holds                                            | Typical source                             |
| --------------------- | ------------------------------------------------ | ------------------------------------------ |
| `pv.PolyData`         | points + surface cells (verts/lines/faces)       | `pv.Sphere()`, STL/OBJ files, point clouds |
| `pv.UnstructuredGrid` | arbitrary cells + data                           | simulations, `.vtu` files                  |
| `pv.ImageData`        | uniform voxel grid (spacing, dimensions, origin) | volumes, images                            |
| `pv.StructuredGrid`   | curvilinear points grid                          | parametric meshes                          |
| `pv.RectilinearGrid`  | axis-aligned variable spacing                    | Cartesian grids                            |

Facts that prevent wrong code:

- `mesh.points` is an `(N, 3)` float array. Modify in place or reassign; never shrink it without rebuilding the mesh.
- `mesh.faces` on `PolyData` is a flat array `[n, i0, i1, i2, n, j0, j1, j2, ...]`. If `mesh.is_all_triangles`, `mesh.faces.reshape(-1, 4)` works; otherwise it does not.
- Build meshes from NumPy with `pv.PolyData(points, faces=...)` or `pv.wrap(array)`.
- Point data: `mesh.point_data["name"] = arr` where `arr.shape[0] == mesh.n_points`. Cell data must match `mesh.n_cells`. Mismatch raises or silently misrenders — check lengths before assigning.
- Filters (`clip`, `slice`, `threshold`, `decimate`, `extract_surface`, `contour`, `smooth_taubin`, `triangulate`) return new meshes. Pass `inplace=True` only when the project already relies on it.
- `mesh.bounds`, `mesh.center`, `mesh.n_points`, `mesh.n_cells` are properties, not methods.

## Plotting essentials

- `add_mesh(mesh, scalars="name", cmap="viridis", clim=[lo, hi], show_edges=True, opacity=0.5)`. PyVista shows `active_scalars` by default; pass `scalars=` explicitly to be deterministic.
- `nan_color` controls how NaN scalars render. Fill NaNs with `np.nan_to_num` or set `nan_color` when a mask is intended.
- Layout: `pv.Plotter(shape=(rows, cols))` then `pl.subplot(r, c)` before each `add_mesh`.
- Cameras: `pl.camera_position = "xy" | "iso" | [pos, focal, viewup]`. Set after adding meshes.
- Text/axes: `pl.add_text`, `pl.add_axes` (orientation widget: `pl.add_axes` replaces deprecated `add_axes` variants; prefer `pl.show_axes()` only when an interactive widget is unwanted).
- Themes: `pv.set_plot_theme("dark")` or tweak `pv.global_theme` (background, fonts, colorbars). Set once at startup, not per figure.

## Headless and off-screen rendering

```python
pl = pv.Plotter(off_screen=True, window_size=(1024, 768))
pl.add_mesh(mesh)
img = pl.screenshot()   # (H, W, 3) uint8 array
```

- Linux CI/containers usually need X: call `pv.start_xvfb()` once before the first render. On Windows/macOS it is unnecessary and errors on Linux-only setups.
- Save figures with `pl.screenshot("out.png")` or `pl.show(screenshot="out.png")`. `window_size` sets pixel size.
- In Jupyter, `pv.set_jupyter_backend("trame")` (interactive), `"static"`, or `"client"`. If trame is missing, the backend falls back to static — do not assume interactivity.

## File I/O

- Read anything VTK reads: `pv.read("mesh.vtu")` — extension decides the reader. Common: `.vtk`, `.vtu`, `.vtp`, `.stl`, `.ply`, `.obj`, `.vtkhdf`.
- Save with `mesh.save("out.vtu")`. Pick the extension that matches the data class (PolyData → `.vtp`/`.stl`/`.ply`; UnstructuredGrid → `.vtu`).
- Round-trip check after nontrivial mesh edits: `assert pv.read(tmp).n_points == mesh.n_points`.

## Typical pitfalls

1. Mutating `mesh.points` after adding the mesh to a plotter does not refresh the render — rebuild or re-add the actor.
2. Faces arrays built with `np.array([...])` of mixed triangle counts produce silent geometry corruption. Use helper constructors (`pv.Box`, `pv.Cylinder`, `pv.Plane`, `pv.Line`) or verified face arrays.
3. `pl.show()` inside scripts on headless machines hangs. Use `off_screen=True`.
4. Scalar range surprises: set `clim` explicitly; VTK auto-range includes outliers.
5. Z-up vs Y-up: PyVista is Z-up. When importing assets from Y-up tools, rotate explicitly, never eyeball.
6. Comparing meshes: compare `points` arrays and cell connectivity, not object identity — filters always allocate new objects.

## Verify before finishing

```python
pl = pv.Plotter(off_screen=True)
pl.add_mesh(mesh)
img = pl.screenshot()
assert img.shape[:2] == (768, 1024)
assert img.any(), "render is blank"
```

Run the code. Judge the render from observed pixels (non-blank, expected silhouette, correct color mapping), never from "the code looks right". If the change is geometry, check `bounds` and `n_points` too. Effort proportional to the task: a color change needs one screenshot; a filter pipeline needs bounds + point/cell counts + screenshot.
