---
name: pyvista-widgets
description: Interactive widgets for PyVista Plotter — slider widgets, text slider widgets, checkbox button widgets, and key event bindings, with callback signatures and off-screen testing patterns. Use when a task adds parameter controls to a PyVista visualization, binds keyboard shortcuts to scene changes, or tests widget callbacks. Do not use for static rendering, mesh processing, or file I/O (use pyvista-plotting, pyvista-filtering, or pyvista-mesh-io).
---

# PyVista Widgets

Widgets are `Plotter` UI controls bound to callbacks. The pattern is always the same: add widget → pass a callback → callback mutates mesh/actor → PyVista re-renders.

## Callback contract

Callbacks take exactly one parameter:

```python
def on_change(value: float) -> None:
    actor.SetScale(1.0, 1.0, value)

pl.add_slider_widget(on_change, rng=[0.0, 2.0], value=1.0, title="scale")
```

- Slider callback receives a `float`; checkbox callback receives the new state.
- Keep callbacks cheap — they run on every interaction frame.

## Widgets

| Widget                 | Call                                                                | Callback arg |
| ---------------------- | ------------------------------------------------------------------- | ------------ |
| Slider                 | `pl.add_slider_widget(cb, rng=[lo, hi], value=v, title="...")`      | `float`      |
| Text slider (discrete) | `pl.add_text_slider_widget(cb, rng=[lo, hi], value=v, title="...")` | `float`      |
| Checkbox button        | `pl.add_checkbox_button_widget(cb, value=False)`                    | state        |
| Key event              | `pl.add_key_event("s", cb)` (no callback arg)                       | —            |

- Slider styling: `color=`, `event_type=` for "always"/"release" updates.
- Removing: `pl.clear_actors()` clears geometry, not widget UI; recreate the `Plotter` to reset the UI.

## Pitfalls

1. Widget callbacks need an active render window. In `off_screen=True` the widget exists but cannot be interacted with — drive logic by calling the callback directly.
2. Callback signature mismatches fail at interaction time, not at widget creation. Match the one-parameter contract.
3. `add_key_event` binds per key; re-binding replaces the old callback.
4. Mutating `mesh.points` inside a callback does not refresh the render — mutate the actor (`actor.SetScale`, `actor.SetPosition`) or re-add the mesh.

## Verify before finishing

Widgets are interaction paths — verify by invoking callbacks directly, then screenshot:

```python
pl = pv.Plotter(off_screen=True)
mesh = pv.Sphere()
actor = pl.add_mesh(mesh)

def on_change(value: float) -> None:
    actor.SetScale(1.0, 1.0, value)

pl.add_slider_widget(on_change, rng=[0.0, 2.0], value=1.0)
on_change(0.5)
img = pl.screenshot()
assert img.any(), "render is blank"
```
