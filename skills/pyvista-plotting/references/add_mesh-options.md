# add_mesh options

Keyword arguments for `Plotter.add_mesh`, grouped by purpose. Every option works as a one-off; set defaults you always want in `pv.global_theme` instead.

## Data mapping

| Kwarg                                    | Effect                                                              |
| ---------------------------------------- | ------------------------------------------------------------------- |
| `scalars="name"`                         | array to color by; explicit beats the `active_scalars` default      |
| `cmap="viridis"`                         | matplotlib colormap name or `list` of colors                        |
| `clim=[lo, hi]`                          | scalar range; set explicitly, VTK auto-range tracks outliers        |
| `below_color=`, `above_color=`           | color for values outside `clim`                                     |
| `nan_color=(r, g, b)`, `nan_opacity=1.0` | render of NaN scalars                                               |
| `flip_scalars=True`                      | reverse colormap direction                                          |
| `rgb=True`                               | treat 3-component scalar arrays as RGB colors                       |
| `categorical=True`                       | discrete colormap for integer categories                            |
| `interpolate_before_map=True`            | map scalars before interpolation (less color bleed)                 |
| `show_scalar_bar=True`                   | colorbar visibility; `scalar_bar_args={}` for title/format/position |

## Appearance

| Kwarg                                                  | Effect                                      |
| ------------------------------------------------------ | ------------------------------------------- |
| `color="tan"`                                          | solid color (ignored when `scalars` is set) |
| `opacity=0.5`                                          | 0–1 or per-point array name                 |
| `show_edges=True`, `edge_color=`                       | wireframe overlay on surfaces               |
| `line_width=`, `point_size=`                           | width in pixels                             |
| `render_points_as_spheres=True`                        | round point markers                         |
| `render_lines_as_tubes=True`                           | cylindrical line segments                   |
| `smooth_shading=True`, `split_sharp_edges=True`        | nicer normals; keep sharp feature edges     |
| `ambient=`, `diffuse=`, `specular=`, `specular_power=` | lighting model                              |
| `culling=True` or `"back"`/`"front"`                   | face culling for closed surfaces            |
| `silhouette=True` or `{}` dict                         | outline silhouette against background       |
| `style="wireframe"` or `"points"`                      | render style without changing the mesh      |
