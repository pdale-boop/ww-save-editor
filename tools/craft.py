"""Craft a test save from a catalog entry, then (optionally) put it in a test build's card.

Run it with no arguments; everything is asked. The source entry is never changed: the
result is a new catalog entry. Uses wwedit.py from the same folder.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import config  # noqa: E402
import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, config.ROOT)
import wwedit  # noqa: E402

CATALOG = config.path('catalog')
INJECT = config.path('inject')


def pick(prompt, options):
    for i, o in enumerate(options, 1):
        print(f'  {i}. {o}')
    while True:
        a = input(prompt).strip()
        if a.isdigit() and 1 <= int(a) <= len(options):
            return int(a) - 1
        print('Please enter one of the numbers shown.')


def pick_entry(prompt, entries):
    """Choose a catalog entry by its own number (the NN at the start of its name)."""
    by_number = {}
    for e in entries:
        name = os.path.basename(os.path.dirname(e))
        print(f'  {name}')
        if name[:2].isdigit():
            by_number[int(name[:2])] = e
    while True:
        a = input(prompt).strip()
        if a.isdigit() and int(a) in by_number:
            return by_number[int(a)]
        print('Please enter the number at the start of an entry.')


def show(s):
    stage, room, point = s.restart()
    print(f'\n  {s.name()}: hearts {s.u16(0x02) / 4:g}/{s.u16(0x00) / 4:g}, rupees {s.u16(0x04)}, '
          f'wallet {s.q[wwedit.WALLET]}, magic {s.q[wwedit.MAGIC_MAX]}, restart {stage} {room} {point}')
    held = [n for n in wwedit.ITEMS_GIVEN if s.has(n)]
    print('  items: ' + (', '.join(held) or 'none'))


def main():
    entries = sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci')))
    src = pick_entry('Start from entry number: ', entries)
    s = wwedit.Save(src, 1)
    print(f'Loaded quest log 1 of {os.path.basename(os.path.dirname(src))}, checksums '
          f'{"ok" if s.checksum_ok() else "BAD"}')
    changes = []
    while True:
        show(s)
        i = pick('Edit: ', ['Give an item', 'Remove an item', 'Hearts', 'Rupees and wallet',
                            'Restart place', 'Set or clear a story flag', 'Done: save as a new entry'])
        if i == 0:
            items = list(wwedit.ITEMS_GIVEN)
            item = items[pick('Item: ', items)]
            s.give(item)
            changes.append(f'gave {item}')
        elif i == 1:
            slot = pick('Slot: ', wwedit.SLOT_NAMES)
            s.take(slot)
            changes.append(f'removed {wwedit.SLOT_NAMES[slot]}')
        elif i == 2:
            m = float(input('Max hearts (e.g. 5 or 5.25): '))
            s.set_hearts(m)
            changes.append(f'hearts {m:g}')
        elif i == 3:
            r = int(input('Rupees: '))
            w = int(input('Wallet size (0: 200, 1: 1000, 2: 5000): '))
            s.set_wallet(w)
            s.set_rupees(min(r, (200, 1000, 5000)[w]))
            changes.append(f'rupees {r}, wallet {w}')
        elif i == 4:
            parts = input('STAGE ROOM POINT (e.g. sea 13 0 for Dragon Roost Island): ').split()
            s.set_restart(parts[0], int(parts[1]), int(parts[2]))
            changes.append(f'restart {" ".join(parts)}')
        elif i == 5:
            v = int(input('Flag (e.g. 0x2902): '), 16)
            on = input(f'Currently {"on" if s.flag(v) else "off"}. Turn it on or off? [on/off]: ').strip() == 'on'
            s.set_flag(v, on)
            changes.append(f'flag 0x{v:04X} {"on" if on else "off"}')
        else:
            break
    if not changes:
        print('No changes; nothing written.')
        return
    numbers = [int(n[:2]) for n in os.listdir(CATALOG) if n[:2].isdigit()]
    label = input('Describe this test save: ').strip() or 'crafted'
    label = ''.join(ch for ch in label if ch not in '\\/:*?"<>|').rstrip(' .')
    out = os.path.join(CATALOG, f'{max(numbers, default=0) + 1:02d} {label} [crafted]')
    os.makedirs(out)
    gci = os.path.join(out, 'GZLE01-gczelda.gci')
    s.save(gci)
    with open(os.path.join(out, 'info.txt'), 'w', encoding='utf-8') as f:
        f.write(f'{label}\ncrafted from {os.path.basename(os.path.dirname(src))} (quest log 1)\n'
                + ''.join(f'- {c}\n' for c in changes))
    print(f'Wrote {out}')
    cards = config.cards()
    if cards and os.path.isfile(INJECT) and input('Put it in a test build\'s card, slot 3? [y/N]: ').lower() == 'y':
        card = cards[pick('Card: ', cards)]
        shutil.copy2(card, card + '.before-craft')
        subprocess.run([INJECT, 'inject', card, gci, '1', '3', card], check=True)
        print(f'Done; the previous card is saved as {card}.before-craft. Load quest log 3.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
