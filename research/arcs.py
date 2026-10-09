"""Story arcs (research/arcs/*.json): where a save sits on each arc.

An arc is an ordered list of steps; each step sets flags, items and stage switches. Optional
flags (`optional_flags`: set only by an optional talk) are set with the step but not checked. A
save is at step n when steps 1..n are all done and no later step is; otherwise it is "mixed". This is the
reading the progress sliders will use (TODO.md, Features). Run it to check the arc files against a
folder of saves (the research catalog by default).
"""
import glob
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import wwedit

ARCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arcs')


def load_arcs(folder=ARCS):
    return [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(folder, '*.json')))]


def switch_on(save, area, no):
    """Saved stage switch (0..0x7F) in an area's dSv_memBit_c: mSwitch[4] at +0x04 (d_save.h)."""
    off = wwedit.MEMORY + area * 0x24 + 4 + (no >> 5) * 4
    return bool(struct.unpack('>I', bytes(save.q[off:off + 4]))[0] & (1 << (no & 31)))


# dSv_memBit_c::mDungeonItem (area block + 0x21) bits, d_save.h: onDungeonItem(i_no) sets 1 << i_no.
DUNGEON_ITEMS = ('MAP', 'COMPASS', 'BOSS_KEY', 'STAGE_BOSS_ENEMY', 'STAGE_LIFE', 'STAGE_BOSS_DEMO')


def dungeon_item(save, area, name):
    return bool(save.q[wwedit.MEMORY + area * 0x24 + 0x21] & (1 << DUNGEON_ITEMS.index(name)))


def has_song(save, name):
    return bool(save.q[wwedit.SONGS] & (1 << wwedit.SONG_NAMES.index(name)))


def has_pearl(save, name):
    return bool(save.q[wwedit.PEARLS] & (1 << wwedit.PEARL_NAMES.index(name)))


def owns(save, item):
    if item in wwedit.ITEMS_GIVEN:
        return save.has(item)
    for index, (_, table) in enumerate(wwedit.EQUIPMENT):
        for name, _, bit in table:
            if name == item and bit is not None:
                return bool(save.q[wwedit.COLLECT + index] & (1 << bit))     # mCollect bits
    raise ValueError(f'unknown item {item!r}')


def step_missing(save, step):
    """What a save lacks of a step: [] when the step is done."""
    sets, missing = step.get('sets', {}), []
    missing += [f for f in sets.get('flags', []) if not save.flag(int(f, 16))]
    missing += [i for i in sets.get('items', []) if not owns(save, i)]
    missing += [f"area {s['area']} switch {s['switch']}" for s in sets.get('switches', [])
                if not switch_on(save, s['area'], int(s['switch'], 16))]
    missing += [p for p in sets.get('pearls', []) if not has_pearl(save, p)]
    missing += [n for n in sets.get('songs', []) if not has_song(save, n)]
    d = sets.get('dungeon_items')
    if d:
        missing += [f"area {d['area']} {i}" for i in d['items'] if not dungeon_item(save, d['area'], i)]
    return missing


def checked_count(step):
    sets = step.get('sets', {})
    return (sum(len(sets.get(k, [])) for k in ('flags', 'items', 'switches', 'pearls', 'songs'))
            + len(sets.get('dungeon_items', {}).get('items', [])))


def position(save, arc):
    """(n, None) when steps 1..n are done and the rest not started; (None, text) when mixed.
    A step with nothing checkable counts as done. Partly done steps count as not done.
    Steps with a window ({"after", "by"}: step ids, "by" optional) are left out of the order and
    checked against it instead: started only once "after" is done, done once "by" is."""
    floating = [s for s in arc['steps'] if 'window' in s]
    steps = [s for s in arc['steps'] if 'window' not in s]
    n, mixed = ordered_position(save, steps)
    if mixed:
        return None, mixed
    ids = [s['id'] for s in steps]
    for s in floating:
        after = ids.index(s['window']['after'])
        by = ids.index(s['window']['by']) if s['window'].get('by') else None
        missing = step_missing(save, s)
        if by is not None and n > by and missing:
            return None, f"past {s['window']['by']}, but {s['id']} lacks {', '.join(missing)}"
        if n <= after and len(missing) < checked_count(s):
            return None, f"{s['id']} started before {s['window']['after']} is done"
    return n, None


def ordered_position(save, steps):
    done = [not step_missing(save, s) for s in steps]
    checked = [checked_count(s) for s in steps]
    started = [c > 0 and len(step_missing(save, s)) < c for s, c in zip(steps, checked)]
    n = 0
    while n < len(steps) and done[n]:
        n += 1
    if not any(started[n:]):
        return n, None
    late = [steps[i]['id'] for i in range(n, len(steps)) if started[i]]
    return None, f"at {steps[n - 1]['id'] if n else 'start'}, but later steps started: {', '.join(late)}"


def main():
    default = r'C:\src\saves\catalog'
    folder = input(f'Folder of saves [{default}]: ').strip() or default
    paths = sorted(glob.glob(os.path.join(folder, '**', '*.gci'), recursive=True))
    if not paths:
        return print('No .gci files found there.')
    arcs = load_arcs()
    print(f'{len(arcs)} arc(s), {len(paths)} save(s).')
    for arc in arcs:
        print(f"\n== {arc['name']} ({len(arc['steps'])} steps, {arc.get('status', '')})")
        for p in paths:
            save = wwedit.Save(p)
            n, mixed = position(save, arc)
            steps = [s for s in arc['steps'] if 'window' not in s]
            where = mixed and f'MIXED: {mixed}' or (steps[n - 1]['id'] if n else 'not started')
            if mixed:
                n_done = 0
                while n_done < len(steps) and not step_missing(save, steps[n_done]):
                    n_done += 1
                if n_done < len(steps):
                    where += f" (first gap: {steps[n_done]['id']} lacks {', '.join(step_missing(save, steps[n_done]))})"
            print(f"  {os.path.basename(os.path.dirname(p))[:44]:44} {where}")


if __name__ == '__main__':
    main()
