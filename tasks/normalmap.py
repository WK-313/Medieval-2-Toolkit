"""Normal maps generated from a diffuse texture, without GIMP.

This is a port of the workflow the unit textures in this project were made
with: the gimp-normalmap plug-in (Shawn Kirst, GPL) driven from Filters > Map >
Normalmap with the "4 sample" filter, scale 4, min Z 0, Invert X and Invert Y,
and Alpha channel: Height - then the layer's alpha moved into a layer mask,
Brightness-Contrast applied to that mask, and the mask applied back down.

Everything here is numpy over an RGBA array, so the export does not need GIMP,
the plug-in, or any external process. Only the "4 sample" filter is ported:
it is the one the reference textures were made with, and it is the one the
panel exposes.

Verified against the reference pairs in Reference/Normal map/Proj: the RGB
comes out at or below the error DXT5 compression alone introduces, and the
alpha within 1/255 on ~90% of pixels.
"""

import numpy as np

# The plug-in's own luminance weights (normalmap.c, CONVERT_NONE). They are not
# Rec.601 - .3/.59/.11 is what it ships, and matching it matters because every
# gradient below is a difference of these values.
LUMA = (0.3, 0.59, 0.11)

# What reproduces the reference textures. The remembered "-127 / 60" does not:
# in GIMP's formula a brightness of -127 multiplies the channel by zero, which
# is a black alpha and therefore no specular at all.
DEFAULT_BRIGHTNESS = -100.0
DEFAULT_CONTRAST = 12.0

# Scale is the plug-in's own "Scale" box: how far the normals tilt, so how deep
# the texture's detail reads in game. 4 is what this project's textures use;
# the reference maps from another modder measure closest at 3.
DEFAULT_SCALE = 4.0


def luminance(rgb):
    """Height field from an RGB(A) uint8 array, 0..1."""
    a = rgb.astype(np.float32)
    return (a[..., 0] * LUMA[0] + a[..., 1] * LUMA[1] + a[..., 2] * LUMA[2]) / 255.0


def normalsFromHeight(height, scale=4.0, minz=0.0, xinvert=True, yinvert=True,
                      wrap=False):
    """The plug-in's FILTER_NONE ("4 sample") kernel.

    du = .5*H(x+1) - .5*H(x-1), dv the same down y, then
    n = normalize(-du*scale, -dv*scale, 1) and the two inverts. `height` must
    be top-down (row 0 at the top) - the sign of dv depends on it, and Blender
    hands out image pixels bottom-up, so callers flip first."""
    if wrap:
        xm1, xp1 = np.roll(height, 1, 1), np.roll(height, -1, 1)
        ym1, yp1 = np.roll(height, 1, 0), np.roll(height, -1, 0)
    else:
        # clamp to the edge, which is what HEIGHT() does with wrap off
        p = np.pad(height, 1, mode="edge")
        xm1, xp1 = p[1:-1, 0:-2], p[1:-1, 2:]
        ym1, yp1 = p[0:-2, 1:-1], p[2:, 1:-1]

    n = np.empty(height.shape + (3,), np.float32)
    n[..., 0] = -(0.5 * xp1 - 0.5 * xm1) * scale
    n[..., 1] = -(0.5 * yp1 - 0.5 * ym1) * scale
    n[..., 2] = 1.0
    n /= np.linalg.norm(n, axis=2, keepdims=True)

    if minz > 0:
        low = n[..., 2] < minz
        n[low, 2] = minz
        n[low] /= np.linalg.norm(n[low], axis=1, keepdims=True)

    if xinvert:
        n[..., 0] = -n[..., 0]
    if yinvert:
        n[..., 1] = -n[..., 1]
    return n


def brightnessContrast(value, brightness, contrast):
    """GIMP's Brightness-Contrast on 0..1 values, sliders in -127..127.

    Brightness scales toward 0 when negative and toward 1 when positive, then
    contrast pivots about 0.5 by tan((c+1)*pi/4) - the same shape and the same
    slider range GIMP uses, so a value dialled in there means the same here."""
    b = max(-127.0, min(127.0, float(brightness))) / 127.0
    c = max(-127.0, min(127.0, float(contrast))) / 127.0
    slant = np.tan((c + 1.0) * np.pi / 4.0)
    value = value * (1.0 + b) if b < 0 else value + (1.0 - value) * b
    return (value - 0.5) * slant + 0.5


def normalMapFromDiffuse(rgb, scale=4.0, minz=0.0, xinvert=True, yinvert=True,
                         wrap=False, brightness=DEFAULT_BRIGHTNESS,
                         contrast=DEFAULT_CONTRAST):
    """Top-down RGB(A) uint8 diffuse -> top-down RGBA uint8 normal map.

    The alpha is the height run through Brightness-Contrast. The game reads a
    normal map's alpha as its specular map, so those two sliders are what
    decide how shiny the unit comes out - they are not a cutout and must not
    be confused with the diffuse alpha, which IS one."""
    height = luminance(rgb)
    n = normalsFromHeight(height, scale, minz, xinvert, yinvert, wrap)

    out = np.empty(rgb.shape[:2] + (4,), np.uint8)
    # (unsigned char)((n + 1) * 127.5) in the plug-in, so this truncates too
    out[..., :3] = np.clip((n + 1.0) * 127.5, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(brightnessContrast(height, brightness, contrast),
                          0.0, 1.0) * 255.0
    return out


def imageToArray(image):
    """A Blender image as a top-down RGBA uint8 array.

    Blender stores pixels bottom-up as floats; the flip puts row 0 at the top,
    which is the order normalsFromHeight expects and the order an image file
    is written in."""
    w, h = image.size
    buf = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(buf)
    a = buf.reshape(h, w, 4)[::-1]
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


def arrayToImage(array, image):
    """Write a top-down RGBA uint8 array back into a Blender image."""
    flipped = array[::-1].astype(np.float32) / 255.0
    image.pixels.foreach_set(flipped.ravel())
    image.update()
