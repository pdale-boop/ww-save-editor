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
    return missing


def position(save, arc):
    """(n, None) when steps 1..n are done and the rest not started; (None, text) when mixed.
    A step with nothing checkable counts as done. Partly done steps count as not done."""
    steps = arc['steps']
    done = [not step_missing(save, s) for s in steps]
    checked = [sum(len(s.get('sets', {}).get(k, [])) for k in ('flags', 'items', 'switches')) for s in steps]
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
            where = mixed and f'MIXED: {mixed}' or (arc['steps'][n - 1]['id'] if n else 'not started')
            if mixed:
                n_done = 0
                while n_done < len(arc['steps']) and not step_missing(save, arc['steps'][n_done]):
                    n_done += 1
                if n_done < len(arc['steps']):
                    where += f" (first gap: {arc['steps'][n_done]['id']} lacks {', '.join(step_missing(save, arc['steps'][n_done]))})"
            print(f"  {os.path.basename(os.path.dirname(p))[:44]:44} {where}")


if __name__ == '__main__':
    main()
