---
name: pyvista-mesh-io
description: Dataset types and file I/O for PyVista — PolyData, UnstructuredGrid, ImageData, StructuredGrid, RectilinearGrid; points and faces array contracts; point_data/cell_data assignment; building meshes from NumPy; reading and saving VTK and mesh formats (vtk, vtu, vtp, stl, ply, obj, vtkhdf). Use when a task constructs meshes from arrays, loads or exports mesh files, fixes faces/points array bugs, or attaches scalar data to a mesh. Do not use for rendering styling or filters (use pyvista-plotting or pyvista-filtering).
---

# PyVista Mesh I/O

Pick the dataset class from the data's shape, then respect its array contracts.

## Datasets

| Class                 | Holds                                            | Typical source                             |
| --------------------- | ------------------------------------------------ | ------------------------------------------ |
| `pv.PolyData`         | points + surface cells (verts/lines/faces)       | `pv.Sphere()`, STL/OBJ files, point clouds |
| `pv.UnstructuredGrid` | arbitrary cells + data                           | simulations, `.vtu` files                  |
| `pv.ImageData`        | uniform voxel grid (spacing, dimensions, origin) | volumes, images                            |
| `pv.StructuredGrid`   | curvilinear points grid                          | parametric meshes                          |
| `pv.RectilinearGrid`  | axis-aligned variable spacing                    | Cartesian grids                            |

## Array contracts

- `mesh.points` is an `(N, 3)` float array. Modify in place or reassign; never shrink it without rebuilding the mesh.
- `mesh.faces` on `PolyData` is a flat array `[n, i0, i1, i2, n, j0, j1, j2, ...]`. If `mesh.is_all_triangles`, `mesh.faces.reshape(-1, 4)` works; otherwise it does not.
- Build meshes from NumPy with `pv.PolyData(points, faces=...)` or `pv.wrap(array)`. For mixed cell types use helper constructors (`pv.Box`, `pv.Cylinder`, `pv.Plane`, `pv.Line`) or verified face arrays — hand-built mixed faces corrupt geometry silently.
- Point data: `mesh.point_data["name"] = arr` where `arr.shape[0] == mesh.n_points`. Cell data must match `mesh.n_cells`. Check lengths before assigning; mismatch raises or misrenders.
- `mesh.bounds`, `mesh.center`, `mesh.n_points`, `mesh.n_cells` are properties, not methods.
- Comparing meshes: compare `points` arrays and cell connectivity, not object identity — filters always allocate new objects.
- Groups of meshes: `pv.MultiBlock({"name": mesh, ...})`.

## File I/O

- Read anything VTK reads: `pv.read("mesh.vtu")` — extension decides the reader. Common: `.vtk`, `.vtu`, `.vtp`, `.stl`, `.ply`, `.obj`, `.vtkhdf`.
- Save with `mesh.save("out.vtu")`. Pick the extension that matches the data class: PolyData → `.vtp`/`.stl`/`.ply`; UnstructuredGrid → `.vtu`; ImageData → `.vti`.
- Round-trip check after nontrivial mesh edits:

```python
reloaded = pv.read(tmp)
assert reloaded.n_points == mesh.n_points
assert np.allclose(reloaded.points, mesh.points)
```

- Coordinate systems: PyVista is Z-up. When importing Y-up assets, rotate explicitly with a transform, never eyeball.
