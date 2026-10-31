---
name: pyvista-plotting
description: Rendering and visualization control for PyVista — add_mesh options (colors, scalars, colormaps, clim, opacity), subplot layouts, camera positioning, text and axes, themes, headless/off-screen rendering, screenshots, and Jupyter backends. Use when a task styles a PyVista render, sets up figures or multi-view layouts, renders headless in scripts or CI, captures screenshots, or fixes rendering artifacts. Do not use for mesh construction, filters, or file format work (use pyvista, pyvista-mesh-io, or pyvista-filtering).
---

# PyVista Plotting

Rendering control in PyVista lives on the `Plotter`. One `Plotter` per figure; `show()` finalizes it.

## add_mesh essentials

```python
pl.add_mesh(
    mesh,
    scalars="temp",      # explicit beats active_scalars default
    cmap="viridis",
    clim=[lo, hi],       # set explicitly; VTK auto-range includes outliers
    show_edges=True,
    opacity=0.5,
)
```

- PyVista shows `active_scalars` by default. Pass `scalars=` to be deterministic.
- `nan_color` controls how NaN scalars render. Fill NaNs with `np.nan_to_num` or set `nan_color` when a mask is intended.
- Full option tables (data mapping, appearance, lighting): [references/add_mesh-options.md](references/add_mesh-options.md)
- Vector fields: use `mesh.glyphs(...)` (see pyvista-filtering), not raw `add_mesh`.

## Layouts

```python
pl = pv.Plotter(shape=(2, 2))
pl.subplot(0, 0)
pl.add_mesh(pv.Sphere())
pl.subplot(1, 1)
pl.add_mesh(pv.Cube())
```

- Call `pl.subplot(r, c)` before the `add_mesh` calls that belong to that view.
- Link views with `pl.link_views()`. Unlink before changing one camera.

## Cameras

- `pl.camera_position = "xy" | "xz" | "iso" | [position, focal_point, viewup]`.
- Set cameras after adding meshes. `pl.reset_camera()` after geometry changes.
- Zoom: `pl.camera.zoom(factor)`. Parallel projection for CAD-like views: `pl.enable_parallel_projection()`.

## Text, axes, backgrounds

- `pl.add_text("label", position="upper_left", font_size=12)`.
- `pl.add_axes()` for the orientation widget; `pl.show_axes()` for a non-interactive axes triad.
- Background: `pl.set_background("white")` or `pv.global_theme.background`. Prefer the theme so every figure matches.

## Headless and off-screen rendering

```python
pl = pv.Plotter(off_screen=True, window_size=(1024, 768))
pl.add_mesh(mesh)
img = pl.screenshot()  # (H, W, 3) uint8 array
```

- Linux CI/containers usually need X: call `pv.start_xvfb()` once before the first render. On Windows/macOS it is unnecessary.
- Save figures with `pl.screenshot("out.png")` or `pl.show(screenshot="out.png")`. `window_size` sets pixel size.
- In Jupyter, `pv.set_jupyter_backend("trame")` (interactive), `"static"`, or `"client"`. If trame is missing, the backend falls back to static — do not assume interactivity.

## Pitfalls

1. `pl.show()` finalizes the plotter. Adding meshes after it fails silently or errors — open a new `Plotter`.
2. Colors look wrong because `clim` auto-ranged to outliers. Set `clim`.
3. Blank screenshot on headless: missing `pv.start_xvfb()` or wrong `window_size`.
4. Screenshots compare differently across VTK versions — assert on shape and non-blankness, not exact pixels.
