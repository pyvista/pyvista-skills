# File formats

`pv.read(path)` picks the reader from the extension; `mesh.save(path)` picks the writer the same way. Choose the extension that matches the dataset class.

## VTK XML formats (round-trip all array data)

| Extension | Dataset class      |
| --------- | ------------------ |
| `.vtp`    | `PolyData`         |
| `.vtu`    | `UnstructuredGrid` |
| `.vti`    | `ImageData`        |
| `.vtr`    | `RectilinearGrid`  |
| `.vts`    | `StructuredGrid`   |

## Legacy and exchange formats

| Extension        | Dataset class      | Notes                                              |
| ---------------- | ------------------ | -------------------------------------------------- |
| `.vtk`           | any                | legacy VTK; readable by everything, keeps all data |
| `.stl`           | `PolyData`         | triangles only, no scalars; CAD exchange           |
| `.ply`           | `PolyData`         | triangles + RGB + scalars                          |
| `.obj`           | `PolyData`         | geometry + texture coordinates only                |
| `.gltf` / `.glb` | `PolyData`         | good for sharing rendered assets                   |
| `.vtkhdf`        | any                | HDF5-backed VTK format                             |
| `.xdmf`          | `UnstructuredGrid` | simulation output; needs matching heavy-data file  |
| `.exodus` / `.e` | `UnstructuredGrid` | requires the `meshio` extra                        |

## Rules of thumb

- For analysis pipelines save `.vtu`/`.vtp` (all arrays survive); export `.stl`/`.obj` only for consumers outside VTK.
- `.stl` strips scalar fields and converts everything to triangles — never use it as an intermediate format for data work.
- Round-trip check after nontrivial edits:

```python
reloaded = pv.read(tmp)
assert reloaded.n_points == mesh.n_points
assert np.allclose(reloaded.points, mesh.points)
```
