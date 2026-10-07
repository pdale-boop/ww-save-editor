"""Gather the evidence for each story flag into one table (research/story-flag-evidence.csv).

For every story flag in tools/wwcat.py's FLAG_BITS it records:
  - where the zeldaret/tww decomp reads it (isEventBit) and writes it (on/off/revEventBit),
    by source file, and whether dComIfG_play_c::getLayerNo reads it (it picks a stage's layer);
  - whether the Wind Waker Randomizer's new-file patch (init_save_with_tweaks in
    asm/patches/custom_funcs.asm) turns it on, and under which option;
  - the first save in the catalog's flag timeline where it turned on;
  - what the editor's current guess (wwgui.mandatory_flag) says.

Only code that names the flag is found: flags read through a variable (an actor parameter from
stage data) or by event and message data on the disc are not. Descriptions from the ZeldaSpeedRuns
sheet are left out of the table on purpose; that sheet must not be committed.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
import config  # noqa: E402
import wwcat   # noqa: E402

OUT = os.path.join(HERE, 'story-flag-evidence.csv')
EVENT = 0x803C522C          # dSv_info_c save.mEvent: the saved event bits
TMP = 0x803C5D60            # dSv_info_c mTmp: temporary bits, not saved
RANDO_OPTIONS = {'sword_mode': 'swordless only', 'num_triforce_shards_to_start_with': '8 starting shards only',
                 'skip_rematch_bosses': 'skip rematch bosses only'}


def ask(prompt, default):
    answer = input(f'{prompt} [{default}]: ').strip().strip('"')
    return answer or default


def enum_names(decomp):
    names = {}
    with open(os.path.join(decomp, 'include', 'd', 'd_save_event_flag.inc'), encoding='utf-8') as f:
        for m in re.finditer(r'(\w+) = (0x[0-9A-Fa-f]{4})', f.read()):
            names.setdefault(m.group(1), int(m.group(2), 16))
    return names


def decomp_uses(decomp, names):
    """{flag: {'read': set(files), 'write': set(files)}} and the flags getLayerNo reads."""
    uses = {}
    call = re.compile(r'(is|on|off|rev)EventBit\(([^;]*)')
    token = re.compile(r'dSv_event_flag_c::(\w+)|\b(0x[0-9A-Fa-f]{4})\b')
    for root, _, files in os.walk(os.path.join(decomp, 'src')):
        for name in files:
            if not name.endswith(('.cpp', '.c', '.inc')):
                continue
            unit = os.path.splitext(name)[0]
            with open(os.path.join(root, name), encoding='utf-8', errors='replace') as f:
                for line in f:
                    for m in call.finditer(line):
                        kind = 'read' if m.group(1) == 'is' else 'write'
                        args = m.group(2).split(')')[0] if 'VERSION_SELECT' not in m.group(2) else m.group(2)
                        for t in token.finditer(args):
                            v = names.get(t.group(1)) if t.group(1) else int(t.group(2), 16)
                            if v is not None:
                                uses.setdefault(v, {'read': set(), 'write': set()})[kind].add(unit)
    with open(os.path.join(decomp, 'src', 'd', 'd_com_inf_game.cpp'), encoding='utf-8') as f:
        text = f.read()
    body = text.split('int dComIfG_play_c::getLayerNo(')[1].split('\n/* 8')[0]
    layer = {names[n] for n in re.findall(r'dSv_event_flag_c::(\w+)', body) if n in names}
    return uses, layer


def rando_new_file(rando):
    """{flag: condition} for the save event bits init_save_with_tweaks turns on."""
    found, base, cond, last = {}, None, None, None
    with open(os.path.join(rando, 'asm', 'patches', 'custom_funcs.asm'), encoding='utf-8') as f:
        lines = f.read().split('init_save_with_tweaks:')[1].split('\n.global ')[0].splitlines()
    for line in lines:
        code = line.split(';')[0].strip()
        if re.match(r'after_\w+:', code):
            cond = None
        m = re.match(r'lis r5, (\w+)@ha', code)
        if m and m.group(1) in RANDO_OPTIONS:
            cond = RANDO_OPTIONS[m.group(1)]
        m = re.match(r'lis r3, (0x[0-9A-Fa-f]{8})@ha', code)
        if m:
            base = int(m.group(1), 16)
        m = re.match(r'li r4, (0x[0-9A-Fa-f]{4})$', code)
        if m:
            last = int(m.group(1), 16)
        if code.startswith('bl onEventBit') and last is not None:
            if base == EVENT:
                found[last] = cond or 'always'
            elif base == TMP:
                found.setdefault(('tmp', last), cond or 'always')
    return found


def timeline_first_on(path):
    """{flag: label of the first save where it turned on} from flag-timeline.txt."""
    first, label = {}, None
    head = re.compile(r'^(.+?)  ->  (.+?): \d+ change')
    flag = re.compile(r'^\s+\+ 0x([0-9A-Fa-f]{4})\s')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = head.match(line)
            if m:
                label = m.group(2)
                continue
            m = flag.match(line)
            if m:
                first.setdefault(int(m.group(1), 16), label)
    return first


def main():
    print('Story flag evidence: decomp code, Randomizer new-file patch, catalog timeline.')
    decomp = ask('zeldaret/tww checkout', '')
    rando = ask('Wind Waker Randomizer checkout', '')
    timeline = ask('Flag timeline', os.path.join(config.path('catalog'), 'flag-timeline.txt'))
    names = enum_names(decomp)
    by_value = {}
    for n, v in names.items():
        by_value.setdefault(v, n)
    uses, layer = decomp_uses(decomp, names)
    rando_flags = rando_new_file(rando)
    first = timeline_first_on(timeline) if os.path.isfile(timeline) else {}
    try:
        import wwgui
        guess = wwgui.mandatory_flag
    except Exception as error:
        print(f'Could not load the editor\'s current guess ({error}); that column is left empty.')
        guess = None

    rows = []
    for v, name, comment in wwcat.FLAG_BITS:
        if (v & 0xFF) == 0xFF or bin(v & 0xFF).count('1') != 1:
            continue                                   # event registers, not single bits
        u = uses.get(v, {'read': set(), 'write': set()})
        rows.append({
            'flag': f'0x{v:04X}',
            'decomp_name': by_value.get(v, name),
            'decomp_note': comment,
            'rando_note': wwcat.WWRANDO_NOTES.get(v, ''),
            'read_by': ' '.join(sorted(u['read'])),
            'written_by': ' '.join(sorted(u['write'])),
            'picks_layer': 'yes' if v in layer else '',
            'rando_new_file': rando_flags.get(v, ''),
            'first_on_in_timeline': first.get(v, ''),
            'current_guess': '' if guess is None else ('required' if guess(v) else 'optional'),
        })
    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tmp = [k[1] for k in rando_flags if isinstance(k, tuple)]
    print(f'{len(rows)} story flags written to {OUT}')
    print(f'  read somewhere in the decomp: {sum(1 for r in rows if r["read_by"])}')
    print(f'  pick a stage layer: {sum(1 for r in rows if r["picks_layer"])}')
    print(f'  set by the Randomizer on a new file: {sum(1 for r in rows if r["rando_new_file"])}')
    print(f'  turned on during the playthrough: {sum(1 for r in rows if r["first_on_in_timeline"])}')
    if tmp:
        print('  the Randomizer also sets temporary (unsaved) bits: ' + ', '.join(f'0x{v:04X}' for v in tmp))


if __name__ == '__main__':
    main()
