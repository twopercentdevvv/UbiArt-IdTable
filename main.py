# based on wukko's implementation - https://github.com/wukko/ubiart-id-table
# platform list from mzommer's ubiartpy - https://github.com/MZommer/UbiArtPY/tree/dev
# if you have any issues with previous games, please make an issue!
import os
import struct
import sys
from collections import Counter

PLATFORMS = [
    "pc", "x360", "ps3", "orbis", "wiiu", "durango", "nx", "ggp", "scarlett", "prospero", "wii",
    # "ctr", "emuwii", "vita", "ipad", "posenet", "blazepose", "unknown", "invalid"
]
BASE = ["bundle", "bundlelogic", "logicbundle", "bootbundlelogic"]
BASE_VALUE = 0
EXTRA_HASH = 0x9CB1BD20
MASK = 0xFFFFFFFF


def mix(a, b, c):
    a = ((a - b - c) ^ (c >> 13)) & MASK
    b = ((b - c - a) ^ (a << 8)) & MASK
    c = ((c - a - b) ^ (b >> 13)) & MASK
    a = ((a - b - c) ^ (c >> 12)) & MASK
    b = ((b - c - a) ^ (a << 16)) & MASK
    c = ((c - a - b) ^ (b >> 5)) & MASK
    a = ((a - b - c) ^ (c >> 3)) & MASK
    b = ((b - c - a) ^ (a << 10)) & MASK
    c = ((c - a - b) ^ (b >> 15)) & MASK
    return a, b, c


def word(d, i):
    return d[i] | (d[i + 1] << 8) | (d[i + 2] << 16) | (d[i + 3] << 24)


def string_id(text):
    d = bytes((c - 32) if 97 <= c <= 122 else c for c in text.encode("utf-8"))
    a = b = 0x9E3779B9
    c = 0
    i = 0
    while len(d) - i >= 12:
        a = (a + word(d, i)) & MASK
        b = (b + word(d, i + 4)) & MASK
        c = (c + word(d, i + 8)) & MASK
        a, b, c = mix(a, b, c)
        i += 12
    c = (c + len(d)) & MASK
    r = d[i:]
    k = len(r)
    if k >= 11: c = (c + (r[10] << 24)) & MASK
    if k >= 10: c = (c + (r[9] << 16)) & MASK
    if k >= 9: c = (c + (r[8] << 8)) & MASK
    if k >= 8: b = (b + (r[7] << 24)) & MASK
    if k >= 7: b = (b + (r[6] << 16)) & MASK
    if k >= 6: b = (b + (r[5] << 8)) & MASK
    if k >= 5: b = (b + r[4]) & MASK
    if k >= 4: a = (a + (r[3] << 24)) & MASK
    if k >= 3: a = (a + (r[2] << 16)) & MASK
    if k >= 2: a = (a + (r[1] << 8)) & MASK
    if k >= 1: a = (a + r[0]) & MASK
    return mix(a, b, c)[2]


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    ipks = [f for f in os.listdir(directory) if f.lower().endswith(".ipk")]

    seen = Counter(f[:-4].rsplit("_", 1)[-1].lower() for f in ipks if "_" in f)
    platform = next((p for p, _ in seen.most_common() if p in PLATFORMS), None)
    if not platform:
        sys.exit("no files found")

    suffix = "_%s.ipk" % platform
    stems = [f[:-len(suffix)] for f in ipks if f.lower().endswith(suffix) and not f.lower().startswith("patch")]
    base = [s for s in stems if s.lower() in BASE]
    rest = sorted((s for s in stems if s.lower() not in BASE), key=str.lower)

    entries = {EXTRA_HASH: 0, string_id("secure_fat.gf"): BASE_VALUE}
    for s in base:
        entries[string_id(s + suffix)] = BASE_VALUE
    for i, s in enumerate(rest):
        entries[string_id(s + suffix)] = BASE_VALUE + 1 + i

    with open(os.path.join(directory, "idtable.idt"), "wb") as f:
        f.write(struct.pack(">I", len(entries)))
        for h in sorted(entries):
            f.write(struct.pack(">Ii", h, entries[h]))


if __name__ == "__main__":
    main()