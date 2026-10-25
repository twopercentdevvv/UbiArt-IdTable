#!/usr/bin/env python3
# if it doesn't work correctly, please make an issue on the repository page!

import os
import struct
import sys
from collections import Counter

out = "idtable.idt"
bext = ".ipk"
sfat = "secure_fat.gf"
ignore = ["patch"] # don't add to idtable
base = ["bundle", "bundlelogic", "logicbundle", "bootbundlelogic"] # bundles the game NEEDS to boot
p = [
    "pc", "x360", "ps3", "orbis", "wiiu", "durango", "nx", "ggp", "scarlett", "prospero", "wii",
    # "ctr", "emuwii", "vita", "ipad", "posenet", "blazepose", "unknown", "invalid"
]


def shifter(a, b, c):
    a = ((a - b - c) ^ (c >> 13)) & 0xFFFFFFFF
    b = ((b - c - a) ^ (a << 8)) & 0xFFFFFFFF
    c = ((c - a - b) ^ (b >> 13)) & 0xFFFFFFFF
    a = ((a - b - c) ^ (c >> 12)) & 0xFFFFFFFF
    b = ((b - c - a) ^ (a << 16)) & 0xFFFFFFFF
    c = ((c - a - b) ^ (b >> 5)) & 0xFFFFFFFF
    a = ((a - b - c) ^ (c >> 3)) & 0xFFFFFFFF
    b = ((b - c - a) ^ (a << 10)) & 0xFFFFFFFF
    c = ((c - a - b) ^ (b >> 15)) & 0xFFFFFFFF
    return a, b, c


def word(d, i):
    return d[i] | (d[i + 1] << 8) | (d[i + 2] << 16) | (d[i + 3] << 24)


def StringID(text):
    d = bytes((c - 32) if 97 <= c <= 122 else c for c in text.encode("utf-8"))
    a = b = 0x9E3779B9
    c = 0
    i = 0
    while len(d) - i >= 12:
        a = (a + word(d, i)) & 0xFFFFFFFF
        b = (b + word(d, i + 4)) & 0xFFFFFFFF
        c = (c + word(d, i + 8)) & 0xFFFFFFFF
        a, b, c = shifter(a, b, c)
        i += 12
    c = (c + len(d)) & 0xFFFFFFFF
    r = d[i:]
    k = len(r)
    if k >= 11: c = (c + (r[10] << 24)) & 0xFFFFFFFF
    if k >= 10: c = (c + (r[9] << 16)) & 0xFFFFFFFF
    if k >= 9: c = (c + (r[8] << 8)) & 0xFFFFFFFF
    if k >= 8: b = (b + (r[7] << 24)) & 0xFFFFFFFF
    if k >= 7: b = (b + (r[6] << 16)) & 0xFFFFFFFF
    if k >= 6: b = (b + (r[5] << 8)) & 0xFFFFFFFF
    if k >= 5: b = (b + r[4]) & 0xFFFFFFFF
    if k >= 4: a = (a + (r[3] << 24)) & 0xFFFFFFFF
    if k >= 3: a = (a + (r[2] << 16)) & 0xFFFFFFFF
    if k >= 2: a = (a + (r[1] << 8)) & 0xFFFFFFFF
    if k >= 1: a = (a + r[0]) & 0xFFFFFFFF
    return shifter(a, b, c)[2]


def IDTable(cwd=None, out=out, bext=bext, sfat=sfat, ignore=ignore, base=base, p=p):
    cwd = cwd or os.getcwd()
    ipks = [f for f in os.listdir(cwd) if f.lower().endswith(bext)]

    seen = Counter(f[:-len(bext)].rsplit("_", 1)[-1].lower() for f in ipks if "_" in f)
    platform = next((x for x, _ in seen.most_common() if x in p), None)
    if not platform:
        raise FileNotFoundError("no files found")

    suffix = "_%s%s" % (platform, bext)
    stems = [
        f[:-len(suffix)] for f in ipks
        if f.lower().endswith(suffix) and not f.lower().startswith(tuple(ignore))
    ]
    bases = [s for s in stems if s.lower() in base]
    rest = sorted((s for s in stems if s.lower() not in base), key=str.lower)

    entries = {0x9CB1BD20: 0, StringID(sfat): 0}
    for s in bases:
        entries[StringID(s + suffix)] = 0
    for i, s in enumerate(rest):
        entries[StringID(s + suffix)] = 1 + i

    path = os.path.join(cwd, out)
    with open(path, "wb") as f:
        f.write(struct.pack(">I", len(entries)))
        for h in sorted(entries):
            f.write(struct.pack(">Ii", h, entries[h]))
    return path


if __name__ == "__main__":
    try:
        IDTable(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    except FileNotFoundError as e:
        sys.exit(str(e))
