#!/usr/bin/env python3
"""Build entry.png for the FrostToast catalogue-photo entry.

Composites two real, freely-licensed Pexels photographs:
- toaster with bread (Pexels 7937466, photo by Nicola Barts) — the base
- two ice cubes on white (Pexels 3675620) — the impossible "toast"

The ice cubes replace the bread slices in the toaster slots, so the picture
reads at a glance as a catalogue shot of a toaster that toasts ice cubes.
Both source photos are Pexels-licensed (free to use); credits are in README.md.
"""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets")


def cube_layer(ice, box, rotate_deg):
    """Cut one ice cube out of the ice photo and return it as an RGBA layer.

    The ice sits on a near-white background, so a luminance threshold gives
    a mask; a scanline fill makes the silhouette solid (ice is translucent,
    so a thin mask would let the bread show through), and a small Gaussian
    blur feathers the edge.
    """
    crop = ice.crop(box)
    lum = np.asarray(crop).astype(np.int16).mean(axis=2)
    mask = (lum < 245).astype(np.uint8)
    # Scanline fill: fill between the first and last set pixel of each row.
    filled = np.zeros_like(mask)
    for y in range(mask.shape[0]):
        xs = np.flatnonzero(mask[y])
        if xs.size:
            filled[y, xs[0] : xs[-1] + 1] = 1
    m = Image.fromarray((filled * 255).astype(np.uint8), "L").filter(
        ImageFilter.GaussianBlur(2.5)
    )
    rgba = crop.convert("RGBA")
    rgba.putalpha(m)
    return rgba.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)


def scale_to(layer, width):
    iw, ih = layer.size
    s = width / iw
    return layer.resize((int(iw * s), int(ih * s)), Image.LANCZOS)


def main():
    toaster = Image.open(os.path.join(ASSETS, "toaster-bread.jpg")).convert("RGB")
    ice = Image.open(os.path.join(ASSETS, "ice.jpg")).convert("RGB")

    # The bread slices lean ~14 degrees (top edge down to the right), so the
    # cubes are rotated to match. Back cube first, front cube over it.
    # The cubes are scaled large so they fully cover the bread slices.
    right = scale_to(cube_layer(ice, (550, 200, 1020, 610), -14), 800)
    left = scale_to(cube_layer(ice, (100, 230, 570, 610), -14), 800)

    comp = toaster.copy()
    rw, rh = right.size
    comp.paste(right, (905 - rw // 2, 780 - rh // 2), right)
    lw, lh = left.size
    comp.paste(left, (700 - lw // 2, 870 - lh // 2), left)

    # Restore the toaster body below the front rim line, so the cubes read as
    # emerging from the slots instead of floating in front of the body.
    rim = Image.new("L", comp.size, 0)
    ImageDraw.Draw(rim).polygon(
        [(0, 734), (1200, 1080), (1200, 1800), (0, 1800)], fill=255
    )
    rim = rim.filter(ImageFilter.GaussianBlur(2))
    comp.paste(toaster, (0, 0), rim)

    # Fit the whole product into a 1024x1024 white canvas (catalogue style).
    out = Image.new("RGB", (1024, 1024), (255, 255, 255))
    small = comp.resize((683, 1024), Image.LANCZOS)
    out.paste(small, (170, 0))
    out.save(os.path.join(ASSETS, "entry-preview.png"))
    print("saved entry-preview.png", out.size)


if __name__ == "__main__":
    main()
