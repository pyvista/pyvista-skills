---
name: pyvista
description: >-
  Entry skill for writing, debugging, and reviewing Python code that uses PyVista
  for 3D visualization, mesh processing, and VTK datasets. Covers imports, Plotter
  lifecycle, dataset routing, and render verification. Use for any task touching
  code that imports pyvista. For focused work prefer the sibling skills:
  pyvista-plotting, pyvista-mesh-io, pyvista-filtering, pyvista-widgets. Do not
  use for matplotlib, general NumPy-only work, or VTK C++ pipelines that do not
  touch the pyvista API.
---

# PyVista

Write the smallest PyVista code that renders the requested result correctly. PyVista is the Pythonic VTK layer: meshes are NumPy-backed objects, filters return new meshes, and rendering goes through `Plotter`.

This skill is the entry point. Route focused work to the sibling skill before writing code:

| Task                                                       | Skill               |
| ---------------------------------------------------------- | ------------------- |
| Rendering, colors, cameras, layouts, screenshots, backends | `pyvista-plotting`  |
| Dataset types, points/faces contracts, file I/O            | `pyvista-mesh-io`   |
| Filters, transformations, glyphs, booleans                 | `pyvista-filtering` |
| Interactive slider/button/key widgets                      | `pyvista-widgets`   |

## Imports and versions

```python
import numpy as np
import pyvista as pv
```

- Check `pv.vtk_version_info()` when behavior differs across VTK. Assume VTK >= 9 and PyVista >= 0.43 unless the project pins otherwise.
- Never import `vtk` directly when `pv` covers the operation. Drop to `vtk` only for features PyVista does not wrap, and say why in a comment.

## Core workflow

```python
mesh = pv.Sphere()  # any PolyData/UnstructuredGrid/...
pl = pv.Plotter()
pl.add_mesh(mesh, color="tan", show_edges=True)
pl.show()
```

1. Build or load the dataset.
2. Create one `Plotter`, add actors with `add_mesh`.
3. Call `pl.show()` (interactive) or `pl.screenshot(path)` (headless).

`pl.show()` finalizes the plotter. Do not add meshes after it. Open a new `Plotter` for the next figure instead of reusing one.

## Invariants that apply everywhere

- Filters return new meshes. Pass `inplace=True` only when the project already relies on it.
- PyVista is Z-up. When importing assets from Y-up tools, rotate explicitly, never eyeball.
- Mutating `mesh.points` after adding the mesh to a plotter does not refresh the render — rebuild or re-add the actor.
- Theme: `pv.set_plot_theme("dark")` or tweak `pv.global_theme`. Set once at startup, not per figure.

## Verify before finishing

```python
pl = pv.Plotter(off_screen=True)
pl.add_mesh(mesh)
img = pl.screenshot()
assert img.shape[:2] == (768, 1024)
assert img.any(), "render is blank"
```

Run the code. Judge the render from observed pixels (non-blank, expected silhouette, correct color mapping), never from "the code looks right". If the change is geometry, check `bounds` and `n_points` too. Effort proportional to the task: a color change needs one screenshot; a filter pipeline needs bounds + point/cell counts + screenshot.
