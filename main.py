#!/usr/bin/env python3
"""news-image-20261122 entrypoint.

Ships the finished Sunday 22 November 2026 news picture. The artwork was
already painted by render.py while the entry was being built, so this
script only hands the finished PNG to the grader. It sticks to the
standard library on purpose: the grading image ships no Pillow, no fonts
and no network, and the same bytes must come out on every run.
"""
import hashlib
import os
import pathlib
import struct
import sys

IMAGE = pathlib.Path(__file__).resolve().parent / "entry.png"
LIMIT_BYTES = 1_048_576
SIZE = (1024, 1024)


def read_png(path):
    """Load entry.png and check its signature, size and dimensions.

    Returns the raw bytes. Raises ValueError on anything the gate would
    refuse: a wrong magic, a missing IHDR chunk, the wrong dimensions,
    or a file over the 1 MiB cap.
    """
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: bad signature")
    if raw[12:16] != b"IHDR":
        raise ValueError("not a PNG file: no IHDR chunk")
    width, height = struct.unpack(">II", raw[16:24])
    if (width, height) != SIZE:
        raise ValueError("image is %dx%d, expected 1024x1024"
                         % (width, height))
    if len(raw) > LIMIT_BYTES:
        raise ValueError("image is %d bytes, over the 1 MiB cap"
                         % len(raw))
    return raw


def ship(destination):
    """Write the picture into destination and prove the copy is exact.

    Returns a short report line. The destination bytes are read back and
    hashed, so a short or corrupted write is caught here instead of
    being handed to the judge.
    """
    raw = read_png(IMAGE)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "entry.png"
    target.write_bytes(raw)
    again = target.read_bytes()
    if again != raw:
        raise ValueError("written file differs from entry.png")
    digest = hashlib.sha256(raw).hexdigest()
    return ("delivered %s 1024x1024 %d bytes sha256=%s"
            % (target, len(raw), digest))


def run():
    out_dir = pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        print(ship(out_dir))
    except (OSError, ValueError) as problem:
        print("error: %s" % problem, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
