#!/usr/bin/env python
"""Headless render verification for PyVista skills and examples.

Renders a mesh off-screen and either checks it against a baseline PNG
or captures one. Useful to verify that skill instructions produce the
expected visual result.

Dependencies: pyvista (pulls in vtk) and numpy.

Usage:

    # Capture a baseline once
    python scripts/render_check.py mesh.vtu --save-baseline expected.png

    # Verify against it (exit 0 = pass, 1 = fail, 2 = usage/env error)
    python scripts/render_check.py mesh.vtu --baseline expected.png

    # No mesh yet? Self-test the environment with a sphere
    python scripts/render_check.py --self-test

    # Without a baseline, --baseline is replaced by --out (just render)
    python scripts/render_check.py mesh.vtp --out actual.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_WINDOW_SIZE = (1024, 768)
DEFAULT_MAX_MEAN_DIFF = 2.0  # per-channel, 0-255


def ensure_display() -> None:
    """Start Xvfb on headless Linux; no-op on Windows/macOS."""
    import pyvista as pv

    if sys.platform == "linux" and not _has_display():
        pv.start_xvfb()


def _has_display() -> bool:
    import os

    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def render(mesh_path: Path, window_size: tuple[int, int]) -> object:
    """Render the mesh off-screen and return the (H, W, 3) uint8 image."""
    import pyvista as pv

    ensure_display()
    mesh = pv.read(mesh_path)
    pl = pv.Plotter(off_screen=True, window_size=window_size)
    pl.add_mesh(mesh)
    pl.reset_camera()
    return pl.screenshot()


def compare(actual: object, baseline_path: Path, max_mean_diff: float) -> list[str]:
    """Return a list of failure reasons (empty when the images match)."""
    import numpy as np
    from PIL import Image

    expected = np.asarray(Image.open(baseline_path).convert("RGB"))
    failures: list[str] = []
    if expected.shape != actual.shape:
        failures.append(
            f"size mismatch: baseline {expected.shape[1]}x{expected.shape[0]}, "
            f"render {actual.shape[1]}x{actual.shape[0]} "
            "(pass --window-size to match the baseline)"
        )
        return failures
    diff = np.abs(expected.astype(int) - actual.astype(int))
    mean_diff = diff.mean()
    if mean_diff > max_mean_diff:
        failures.append(
            f"mean pixel diff {mean_diff:.2f} exceeds {max_mean_diff} "
            f"(max channel diff {diff.max():.0f})"
        )
    return failures


def self_test() -> int:
    """Render a sphere and assert the output is not blank."""
    import pyvista as pv

    ensure_display()
    pl = pv.Plotter(off_screen=True, window_size=DEFAULT_WINDOW_SIZE)
    pl.add_mesh(pv.Sphere(), color="tan")
    img = pl.screenshot()
    if img.shape[:2] != DEFAULT_WINDOW_SIZE[::-1]:
        print(f"FAIL: expected {DEFAULT_WINDOW_SIZE[::-1]}, got {img.shape[:2]}")
        return 1
    if not img.any():
        print("FAIL: render is blank")
        return 1
    print(f"OK: sphere rendered, image {img.shape[1]}x{img.shape[0]}, non-blank")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("mesh", nargs="?", type=Path, help="mesh file to render")
    parser.add_argument("--baseline", type=Path, help="expected PNG to compare against")
    parser.add_argument("--save-baseline", type=Path, help="capture a baseline PNG")
    parser.add_argument("--out", type=Path, help="write the render to this PNG")
    parser.add_argument(
        "--window-size",
        default=f"{DEFAULT_WINDOW_SIZE[0]}x{DEFAULT_WINDOW_SIZE[1]}",
        help="render size as WIDTHxHEIGHT (default 1024x768)",
    )
    parser.add_argument(
        "--max-mean-diff",
        type=float,
        default=DEFAULT_MAX_MEAN_DIFF,
        help=f"failure threshold for mean pixel diff (default {DEFAULT_MAX_MEAN_DIFF})",
    )
    parser.add_argument(
        "--self-test", action="store_true", help="render a sphere and check it is non-blank"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.mesh is None:
        parser.error("a mesh file (or --self-test) is required")

    try:
        window_size = tuple(int(v) for v in args.window_size.lower().split("x"))
        if len(window_size) != 2 or not all(window_size):
            raise ValueError
    except ValueError:
        print(f"error: --window-size must look like 1024x768, got {args.window_size!r}")
        return 2

    if not args.mesh.exists():
        print(f"error: mesh not found: {args.mesh}")
        return 2

    try:
        img = render(args.mesh, window_size)
    except Exception as exc:  # noqa: BLE001 — report any render failure verbatim
        print(f"error: rendering {args.mesh} failed: {exc}")
        print(
            "hint: on headless Linux, install xvfb (apt install xvfb) — "
            "this script calls pv.start_xvfb() automatically"
        )
        return 2

    if args.out:
        import pyvista as pv  # noqa: F401 — ensures vtk libs are loaded first
        from PIL import Image

        Image.fromarray(img).save(args.out)
        print(f"render written: {args.out}")

    if args.save_baseline:
        from PIL import Image

        Image.fromarray(img).save(args.save_baseline)
        print(f"baseline written: {args.save_baseline}")
        return 0

    if args.baseline:
        if not args.baseline.exists():
            print(f"error: baseline not found: {args.baseline}")
            print(f"hint: create it first with --save-baseline {args.baseline}")
            return 2
        failures = compare(img, args.baseline, args.max_mean_diff)
        if failures:
            for reason in failures:
                print(f"FAIL: {reason}")
            return 1
        print(f"OK: render matches {args.baseline}")
        return 0

    if not args.out:
        print("error: nothing to do — pass --baseline, --save-baseline, or --out")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
