"""Make a copy of a catalog save with the sea chart as a vanilla game would have it.

Better Wind Waker's "Reveal full sea chart" (wwrando patch reveal_sea_chart.asm) makes
a new file start with every sea square drawn: it sets bit 0 of every island's entry in
dSv_player_map_c::mFmapBits. In a vanilla game bit 0 is only set for Forsaken Fortress,
Windfall and Outset at file creation (dSv_player_map_c::init), and later when a fishman
draws a square (dMenu_Fmap_c::fmDispArea). Bit 1, "Link has sailed here", is untouched.

This clears bit 0 everywhere except those three defaults. That is exactly vanilla up to
the first fishman; after that, squares fishmen drew are lost too. Run it with no
arguments; it asks which entry to copy and writes a new entry. The original is untouched.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import config  # noqa: E402
import glob
import os
import struct

CATALOG = config.path('catalog')
BLOCK, QUEST, DATA, HEADER = 0x2000, 0x770, 0x768, 64
FMAP = 0xBF + 0x40            # mFmapBits in the card quest log, 49 islands
DEFAULTS = (0, 10, 43)        # Forsaken Fortress, Windfall, Outset


def qsum(q):
    total = sum(q[:DATA]) & 0xFFFFFFFF
    inverse = sum(~b & 0xFFFFFFFF for b in q[:DATA]) & 0xFFFFFFFF
    return total << 32 | inverse


def block_checksum(block):
    total = inverse = 0
    for i in range(0, BLOCK - 4, 2):
        word = block[i] << 8 | block[i + 1]
        total = (total + word) & 0xFFFF
        inverse = (inverse + (~word & 0xFFFF)) & 0xFFFF
    return total << 16 | inverse


def main():
    entries = sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci')))
    names = [os.path.basename(os.path.dirname(e)) for e in entries]
    for i, n in enumerate(names, 1):
        print(f'  {i}. {n}')
    while True:
        a = input('Entry to copy with a vanilla sea chart: ').strip()
        if a.isdigit() and 1 <= int(a) <= len(entries):
            break
        print('Please enter one of the numbers shown.')
    src = entries[int(a) - 1]
    d = bytearray(open(src, 'rb').read())
    changed = 0
    for copy in (0, 1):
        block = HEADER + BLOCK * (1 + copy)
        q = block + 8                          # quest log 1
        for isle in range(49):
            if isle in DEFAULTS:
                continue
            if d[q + FMAP + isle] & 1:
                d[q + FMAP + isle] &= 0xFE
                changed += copy == 0
        d[q + DATA:q + DATA + 8] = struct.pack('>Q', qsum(d[q:q + QUEST]))
        d[block + BLOCK - 4:block + BLOCK] = struct.pack('>I', block_checksum(d[block:block + BLOCK]))
    numbers = [int(n[:2]) for n in os.listdir(CATALOG) if n[:2].isdigit()]
    name = f'{max(numbers, default=0) + 1:02d} {names[int(a) - 1].split(" ", 1)[1]} [vanilla chart]'
    out = os.path.join(CATALOG, name)
    os.makedirs(out)
    open(os.path.join(out, 'GZLE01-gczelda.gci'), 'wb').write(d)
    with open(os.path.join(out, 'info.txt'), 'w', encoding='utf-8') as f:
        f.write(f'{name}\ncopy of {names[int(a) - 1]} with the sea chart reset to vanilla '
                f'(cleared {changed} drawn squares; kept Forsaken Fortress, Windfall, Outset)\n')
    print(f'Cleared {changed} drawn squares. Wrote {out}')


if __name__ == '__main__':
    main()
