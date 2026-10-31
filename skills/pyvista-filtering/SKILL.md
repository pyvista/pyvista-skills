---
name: pyvista-filtering
description: Mesh processing and transformation for PyVista — filters such as clip, slice, threshold, contour, decimate, subdivide, smooth_taubin, extract_surface, triangulate; glyphs for vector fields; boolean operations on PolyData. Use when a task processes, transforms, decimates, cleans, or analyzes mesh geometry, visualizes vector fields, or pipelines multiple filters. Do not use for plotting styling, widget UI, or file format work (use pyvista-plotting, pyvista-widgets, or pyvista-mesh-io).
---

# PyVista Filtering

Filters are the PyVista processing API. They allocate new meshes; the original is untouched.

## Filter semantics

- Filters return new meshes. Pass `inplace=True` only when the project already relies on it.
- Chaining is normal: `mesh.extract_surface().smooth_taubin().decimate(0.5)`.
- Comparing meshes: compare `points` arrays and cell connectivity, not object identity.

## Common filters

| Filter                                                           | Use                                                                  |
| ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| `extract_surface()`                                              | volume grid → surface `PolyData`                                     |
| `triangulate()`                                                  | force all triangles                                                  |
| `decimate(target_reduction=0.5)`                                 | reduce triangle count                                                |
| `subdivide(nsub=2)`                                              | refine mesh                                                          |
| `smooth_taubin(...)`                                             | smooth without shrinking (Laplacian alternative: `smooth()` shrinks) |
| `clip(normal="x", origin=...)` or `clip(scalar=..., invert=...)` | cut with plane or scalar field                                       |
| `slice(normal="z", origin=...)`                                  | extract cross-section                                                |
| `threshold(value=[lo, hi], scalars="name")`                      | keep cells in scalar range                                           |
| `contour(isosurfaces=..., scalars="name")`                       | isosurfaces from volume data                                         |
| `cell_centers()`                                                 | cell centroid points                                                 |

- `clip`/`slice` accept a plane (`normal=`, `origin=`, `crinkle=`) or a scalar field (`scalar=`, `value=`).
- `threshold` on point data interpolates; on cell data it selects whole cells (`preference="cell"`).

## Vector fields and glyphs

```python
arrows = mesh.glyph(orient="vectors", scale="vectors", factor=0.1)
pl.add_mesh(arrows)
```

- Glyph sources: `pv.Arrow()`, `pv.Cone()`, `pv.Sphere()`. Pass `orient=` and `scale=` as the vector data array name.
- Add the glyph mesh, not the base mesh, or nothing will show.

## Booleans (PolyData)

- `a.boolean_union(b)`, `a.boolean_difference(b)`, `a.boolean_intersection(b)`.
- Inputs must be manifold, closed surfaces. Watertightness check: `mesh.is_manifold` and volume sign via `mesh.volume > 0`.

## Pitfalls

1. Scalar range surprises when coloring: set `clim` explicitly in `add_mesh`; VTK auto-range includes outliers.
2. `threshold`/`clip` on point vs cell data changes results — know which array you filter on.
3. Boolean ops fail on non-watertight meshes; `clean()` and `triangulate()` first.
4. Verify geometry after pipelines: check `bounds`, `n_points`, `n_cells` against expectations.

```python
result = mesh.extract_surface().triangulate().decimate(0.9)
assert result.n_points < mesh.n_points
assert np.all(np.abs(result.bounds) <= np.max(np.abs(mesh.bounds)) + 1e-6)
```
