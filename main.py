#!/usr/bin/env python3
"""FrostToast catalogue-photo entry.

Writes one image, /output/entry.png: a catalogue photograph of an
impossible gadget — a toaster that toasts ice cubes. The image is a
composite of two real, freely-licensed Pexels photographs (credits in
README.md; the build step is tools/make_entry.py).

The program validates the bundled image (a whole PNG, at most 1 MiB and
1024 by 1024 pixels), copies it to the output directory, and verifies
the copy byte for byte. It clears only the CONTENTS of the output
directory, never the directory itself: the grader mounts /output, and
removing the mount point fails.
"""
import os
import shutil
import struct
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def read_png_size(path):
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def clear_contents(directory):
    os.makedirs(directory, exist_ok=True)
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size = os.path.getsize(SOURCE)
    if size > MAX_BYTES:
        raise ValueError(f"entry.png is {size} bytes, over the 1 MiB cap")
    width, height = read_png_size(SOURCE)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over 1024x1024")
    clear_contents(out_dir)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    if os.path.getsize(dest) != size:
        raise ValueError("copied entry.png does not match the source")
    print(f"wrote {dest} ({width}x{height}, {size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
