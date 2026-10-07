r"""Build the story presets the editor offers, from catalog entries.

Run it with no arguments. It lists the catalog, asks which entries to turn into presets and
what to call each one, and copies them to the presets folder (NN.gci plus presets.json).
The list is saved after every addition, so closing the window part-way loses nothing.
Preset files that are missing from the list (from an interrupted run) are offered back,
matched to the catalog entry they came from.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import config  # noqa: E402
import glob
import json
import os
import shutil

CATALOG = config.path('catalog')
PRESETS = config.path('presets')          # where the editor looks for them


def save_index(presets):
    presets.sort(key=lambda p: p['file'])
    with open(os.path.join(PRESETS, 'presets.json'), 'w', encoding='utf-8') as f:
        json.dump(presets, f, indent=1)


def ask_name(default):
    title = input(f'  Preset name (what players see) [{default}]: ').strip() or default
    return title


def main():
    entries = {}
    for gci in sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci'))):
        name = os.path.basename(os.path.dirname(gci))
        if name[:2].isdigit():
            entries[int(name[:2])] = (name, gci)
    os.makedirs(PRESETS, exist_ok=True)
    try:
        presets = json.load(open(os.path.join(PRESETS, 'presets.json'), encoding='utf-8'))
    except (OSError, ValueError):
        presets = []

    # Recover preset files that never made it into the list.
    listed = {p['file'] for p in presets}
    orphans = sorted(f for f in os.listdir(PRESETS) if f.lower().endswith('.gci') and f not in listed)
    if orphans:
        print(f'{len(orphans)} preset file(s) are missing from the list; naming them now.')
        by_bytes = {open(gci, 'rb').read(): name for name, gci in entries.values()}
        for file in orphans:
            source = by_bytes.get(open(os.path.join(PRESETS, file), 'rb').read())
            default = source[3:] if source else file
            print(f'\n{file}: ' + (f'same as catalog entry "{source}"' if source else 'no matching catalog entry'))
            title = ask_name(default)
            presets = [p for p in presets if p['name'] != title]
            presets.append({'name': title, 'file': file, 'slot': 1, 'source': source or ''})
            save_index(presets)
            print(f'  Added "{title}".')

    print()
    for n in sorted(entries):
        print(f'  {entries[n][0]}')
    print(f'\n{len(presets)} preset(s) so far.')
    while True:
        answer = input('Entry number to add as a preset (Enter when done): ').strip()
        if not answer:
            break
        if not answer.isdigit() or int(answer) not in entries:
            print('Please enter the number at the start of an entry.')
            continue
        name, gci = entries[int(answer)]
        if 'mid-' in name or 'experimental' in name or '[crafted]' in name:
            print('  Note: that entry was made mid-event or crafted; a clean save makes a better preset.')
        title = ask_name(name[3:])
        used = [int(f[:2]) for f in os.listdir(PRESETS) if f[:2].isdigit()]
        file = f'{max(used, default=0) + 1:02d}.gci'
        shutil.copy2(gci, os.path.join(PRESETS, file))
        presets = [p for p in presets if p['name'] != title]
        presets.append({'name': title, 'file': file, 'slot': 1, 'source': name})
        save_index(presets)
        print(f'  Added "{title}".')
    print(f'{len(presets)} preset(s) in {PRESETS}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
