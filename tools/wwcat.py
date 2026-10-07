"""Browse BlueWake save states, view them in BlueWake, and catalog them as saves.

Run it with no arguments. For each state you pick it shows what the state holds,
opens it in BlueWake so you can see where Link is (close BlueWake when done),
then asks whether to catalog it. Cataloging builds the save the game would write
at that moment, straight from the state's RAM (see quest_from_state), so no
in-game saving is needed. Nothing it reads is modified.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import config  # noqa: E402
import glob
import gzip
import os
import struct
import subprocess
import time

STATES = config.path('states')
CATALOG = config.path('catalog')
TEMPLATE = _os.path.join(CATALOG, 'template.gci')     # any exported save; catalog entries are used if absent
EVENT_MODE = 0x803C9EA2           # play.mEvtCtrl.mMode
EVENT_NAMES = {0: 'none', 1: 'talking', 2: 'cutscene', 3: 'scripted event'}

MEM1 = 0x80000000
INFO = 0x803C4C08                 # g_dComIfG_gameInfo.info (dSv_info_c)
STAGINFO_PTR = 0x803C9DA0         # play.mStageData.mpStagInfo
BLOCK, QUEST, DATA, HEADER = 0x2000, 0x770, 0x768, 64

# (in-memory offset, card offset, size, field) from dSv_save_c / dSv_save_c_PACKED
PACK = [
    (0x000, 0x000, 0x18, 'status A (hearts, rupees, equipment)'),
    (0x018, 0x018, 0x18, 'status B (save time, etc.)'),
    (0x030, 0x030, 0x0C, 'restart place'),
    (0x03C, 0x03C, 0x15, 'items'),
    (0x051, 0x051, 0x15, 'items obtained'),
    (0x066, 0x066, 0x08, 'item counts'),
    (0x06E, 0x06E, 0x08, 'item maximums'),
    (0x076, 0x076, 0x18, 'bag items'),
    (0x090, 0x08E, 0x0C, 'bag items obtained'),
    (0x09C, 0x09A, 0x18, 'bag item counts'),
    (0x0B4, 0x0B2, 0x0D, 'collection (songs, shards, pearls)'),
    (0x0C4, 0x0BF, 0x84, 'map and charts'),
    (0x148, 0x143, 0x5C, 'player info (name, clear count)'),
    (0x1A4, 0x19F, 0x05, 'options'),
    (0x1AC, 0x1A4, 0x10, 'priest'),
    (0x1BC, 0x1B4, 0x1C0, 'status C'),
    (0x380, 0x374, 0x240, 'per-area progress'),
    (0x5C0, 0x5B4, 0x64, 'ocean'),
    (0x624, 0x618, 0x100, 'story flags'),
    (0x724, 0x718, 0x50, 'reserve'),
]


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


def read_ram(path):
    """Return the MEM1 bytes of a .bwstate."""
    with gzip.open(path, 'rb') as f:
        if f.read(12)[:8] != b'BWSTATE1':
            raise ValueError('not a BlueWake save state')
        while True:
            raw = f.read(24)
            if len(raw) < 24:
                raise ValueError('no MEM1 chunk')
            tag = raw[:16].rstrip(b'\0')
            size = struct.unpack('<Q', raw[16:])[0]
            if tag == b'MEM1':
                return f.read(size)
            if tag in (b'END', b''):
                raise ValueError('no MEM1 chunk')
            f.read(size)


def ram(mem, addr, size):
    return mem[addr - MEM1:addr - MEM1 + size]


PLAY = INFO + 0x12A0              # g_dComIfG_gameInfo.play
CUR_STAGE = PLAY + 0x3E94         # play.mCurStage: name[8], s16 point, s8 room, s8 layer
STAGE_DT = PLAY + 0x3EB0          # play.mStageData
MAPINFO_PTR = STAGE_DT + 0x14     # mpMapInfo
SCLS_PTR = STAGE_DT + 0x4C        # mpScls

# dComIfGs_setGameStartStage: the first of these story flags that is set decides
# the restart place; past RODE_KORL it depends on where Link is.
START_RULES = [
    (0x2A08, None, 0, 0),          # RODE_KORL: depends on the current area
    (0x0F80, 'sea', 11, 128),      # MET_KORL: Windfall
    (0x0801, 'MajyuE', 0, 0),
    (0x0808, 'MajyuE', 0, 18),
    (0x2401, 'A_umikz', 0, 204),
]


def event_bit(save, flag):
    return bool(save[0x624 + (flag >> 8)] & (flag & 0xFF))


def event_reg(save, reg):
    return save[0x624 + (reg >> 8)] & (reg & 0xFF)


def cstr(b):
    return b.split(b'\0')[0].decode('ascii', 'replace')


def pointer(mem, addr):
    p = struct.unpack('>I', ram(mem, addr, 4))[0]
    return p if MEM1 <= p < MEM1 + len(mem) else None


def compute_restart(mem, save, stag):
    """Return (stage, room, point, how) like dComIfGs_setGameStartStage.
    how is 'exact' or a reason the result is an approximation."""
    for flag, stage, room, point in START_RULES:
        if event_bit(save, flag):
            if stage is not None:
                return stage, room, point, 'exact'
            break
    else:
        return 'sea', 44, 128, 'exact'
    if stag is None:
        return None
    st_type = (struct.unpack('>I', ram(mem, stag + 0x0C, 4))[0] >> 16) & 7
    stage_no = (ram(mem, stag + 9, 1)[0] >> 1) & 0x7F
    current = cstr(ram(mem, CUR_STAGE, 8))
    if current == 'PShip':
        return 'sea', event_reg(save, 0xC3FF), event_reg(save, 0x85FF), 'exact'
    if st_type in (1, 3, 6) or stage_no == 9:
        scls = pointer(mem, SCLS_PTR)
        entries = scls and pointer(mem, scls + 4)
        if entries:
            e = ram(mem, entries, 12)
            return cstr(e[:8]), struct.unpack('b', e[9:10])[0], e[8], 'exact'
        return None
    if stage_no in (11, 12, 13):
        info = pointer(mem, MAPINFO_PTR)
        if info:
            xz = ram(mem, info + 0x36, 1)[0]
            x, z = xz & 0xF, (xz >> 4) & 0xF
            x, z = (x - 16 if x & 8 else x), (z - 16 if z & 8 else z)
            return 'sea', 4 + x + (z + 3) * 7, 0, 'exact'
        return None
    if st_type == 7:
        room = struct.unpack('b', ram(mem, CUR_STAGE + 10, 1))[0]
        return 'sea', room, 0, "approximate: at sea the game uses Link's exact position"
    if stage_no == 10:
        return None
    return 'sea', 11, 0, 'exact'


def quest_from_state(path):
    """Build the 0x770-byte card quest log the game would save at this state.
    Returns (quest, save table number, (stage, room, point, how) or None)."""
    mem = read_ram(path)
    save = bytearray(ram(mem, INFO, 0x778))
    live = ram(mem, INFO + 0x778, 0x24)
    stag = pointer(mem, STAGINFO_PTR)
    stage_no = None
    if stag is not None:
        stage_no = (ram(mem, stag + 9, 1)[0] >> 1) & 0x7F
        if stage_no < 16:
            save[0x380 + stage_no * 0x24:0x380 + (stage_no + 1) * 0x24] = live
        else:
            stage_no = None
    restart = compute_restart(mem, save, stag)
    if restart:
        save[0x30:0x38] = restart[0].encode('ascii')[:7].ljust(8, b'\0')
        save[0x38] = restart[1] & 0xFF
        save[0x39] = restart[2]
    q = bytearray(QUEST)
    for src, dst, size, _ in PACK:
        q[dst:dst + size] = save[src:src + size]
    if struct.unpack('>H', q[2:4])[0] < 12:
        q[2:4] = struct.pack('>H', 12)
    # Save time (status B's first field, OSTime: 40.5 MHz ticks since 2000, local time).
    # The game stamps the moment it saves; use the moment the state was made.
    made = os.path.getmtime(path)
    local = made + time.localtime(made).tm_gmtoff
    q[0x18:0x20] = struct.pack('>Q', int((local - 946684800) * 40500000))
    q[DATA:DATA + 8] = struct.pack('>Q', qsum(q))
    return bytes(q), stage_no, restart


def set_restart(q, stage, room, point):
    q = bytearray(q)
    q[0x30:0x38] = stage.encode('ascii')[:7].ljust(8, b'\0')
    q[0x38] = room & 0xFF
    q[0x39] = point
    q[DATA:DATA + 8] = struct.pack('>Q', qsum(q))
    return bytes(q)


def template_path():
    """Any Wind Waker .gci to borrow the file header and other slots from."""
    for p in [TEMPLATE] + sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci'))):
        if os.path.isfile(p):
            return p
    raise SystemExit('No Wind Waker .gci found to use as a template: export one with '
                     'card_to_gci.py to ' + TEMPLATE)


def write_gci(quest, out_path):
    """Put the quest log into slot 1 (both copies) of a copy of the template save."""
    d = bytearray(open(template_path(), 'rb').read())
    for copy in (0, 1):
        block = HEADER + BLOCK * (1 + copy)
        d[block + 8:block + 8 + QUEST] = quest
        d[block + BLOCK - 4:block + BLOCK] = struct.pack('>I', block_checksum(d[block:block + BLOCK]))
    open(out_path, 'wb').write(d)


def field_of(offset):
    for _, dst, size, name in PACK:
        if dst <= offset < dst + size:
            return name, offset - dst
    return 'checksum', offset - DATA


def compare(state_path, gci_path, slot):
    mine, stage_no, _ = quest_from_state(state_path)
    d = open(gci_path, 'rb').read()
    theirs = d[HEADER + BLOCK + 8 + (slot - 1) * QUEST:][:QUEST]
    print(f'Current area save table number: {stage_no}')
    diffs = [i for i in range(QUEST) if mine[i] != theirs[i]]
    if not diffs:
        print('Identical: the extracted save matches the game\'s save byte for byte.')
        return
    groups = {}
    for i in diffs:
        name, off = field_of(i)
        groups.setdefault(name, []).append((off, theirs[i], mine[i]))
    print(f'{len(diffs)} bytes differ:')
    for name, items in groups.items():
        shown = ', '.join(f'+0x{o:X} {a:02X}->{b:02X}' for o, a, b in items[:8])
        more = f' (+{len(items) - 8} more)' if len(items) > 8 else ''
        print(f'  {name}: {shown}{more}')
    print('(game save -> extracted). Status B and the checksum are expected to differ:')
    print('the game stamps the time it saved, which a state taken earlier cannot know.')
    print('The restart place can also differ if Link moved before you saved in game.')



def pick(prompt, options, allow_quit=False):
    for i, o in enumerate(options, 1):
        print(f'  {i}. {o}')
    while True:
        a = input(prompt).strip().lower()
        if allow_quit and a in ('q', ''):
            return None
        if a.isdigit() and 1 <= int(a) <= len(options):
            return int(a) - 1
        print('Please enter one of the numbers shown' + (', or q.' if allow_quit else '.'))


def summary(path):
    mem = read_ram(path)
    q, stage_no, restart = quest_from_state(path)
    max_life, life, rupee = struct.unpack('>HHH', q[0:6])
    current = ram(mem, 0x803C9D3C, 8).split(b'\0')[0].decode('ascii', 'replace')
    room = struct.unpack('b', ram(mem, 0x803C9D3C + 10, 1))[0]
    event = ram(mem, EVENT_MODE, 1)[0]
    col = q[0xB2:0xBF]
    flags = sum(bin(b).count('1') for b in q[0x618:0x718])
    if restart is None:
        where = (f'save restarts at {cstr(q[0x30:0x38])} room {struct.unpack("b", q[0x38:0x39])[0]} '
                 f'point {q[0x39]} (kept from memory: could not work out where the game would put it)')
    else:
        where = f'save restarts at {restart[0]} room {restart[1]} point {restart[2]}'
        if restart[3] != 'exact':
            where += f' ({restart[3]})'
    text = (f'area {current} room {room}, {where}\n'
            f'hearts {life / 4:g}/{max_life / 4:g}, rupees {rupee}, songs {bin(col[9]).count("1")}, '
            f'shards {bin(col[10]).count("1")}, pearls {bin(col[11]).count("1")}, story bits {flags}\n'
            f'event running: {EVENT_NAMES.get(event, f"mode {event}")}')
    return text, q, event, restart


def cataloged_states():
    done = {}
    for info in glob.glob(os.path.join(CATALOG, '*', 'info.txt')):
        for line in open(info, encoding='utf-8'):
            if line.startswith('state: '):
                done[line[7:].strip()] = os.path.basename(os.path.dirname(info))
    return done


def choose_build():
    exes = sorted(config.bluewake_exes())
    if not exes:
        raise SystemExit('No BlueWake builds found; add your checkout to "bluewake_checkouts" in config.json.')
    print('Which BlueWake should open the states?')
    return exes[pick('Build [1]: ', exes, allow_quit=True) or 0]


def catalog(state, q, text, event):
    os.makedirs(CATALOG, exist_ok=True)
    numbers = [int(n[:2]) for n in os.listdir(CATALOG) if n[:2].isdigit()]
    number = max(numbers, default=0) + 1
    label = os.path.splitext(state)[0]
    label = label[16:].split(' (quick-')[0] if label[:4].isdigit() else label
    name = input(f'Describe this point [{label}]: ').strip() or label
    if event:
        name += f' [mid-{EVENT_NAMES.get(event, "event")}]'
    name = ''.join(ch for ch in name if ch not in '\\/:*?"<>|').rstrip(' .')
    print(f'Restart place: {cstr(q[0x30:0x38])} room {struct.unpack("b", q[0x38:0x39])[0]} point {q[0x39]}')
    change = input('Press Enter to keep it, or type STAGE ROOM POINT to change it: ').split()
    if len(change) == 3:
        q = set_restart(q, change[0], int(change[1]), int(change[2]))
        text += f'\nrestart changed by hand to {change[0]} room {change[1]} point {change[2]}'
    entry = os.path.join(CATALOG, f'{number:02d} {name}')
    os.makedirs(entry)
    try:
        write_gci(q, os.path.join(entry, 'GZLE01-gczelda.gci'))
    except BaseException:
        import shutil
        shutil.rmtree(entry, ignore_errors=True)
        raise
    with open(os.path.join(entry, 'info.txt'), 'w', encoding='utf-8') as f:
        f.write(f'{name}\nstate: {state}\nmade from the state (quest log 1)\n\n{text}\n')
    print(f'Saved entry {number:02d}: {entry}')


def browse():
    exe = choose_build()
    while True:
        states = sorted(glob.glob(os.path.join(STATES, '*.bwstate')), key=os.path.getmtime)
        done = cataloged_states()
        print()
        names = [os.path.basename(s) + (f'   [cataloged: {done[os.path.basename(s)]}]'
                 if os.path.basename(s) in done else '') for s in states]
        i = pick('State to look at (q to quit): ', names, allow_quit=True)
        if i is None:
            return
        state = states[i]
        print(f'\nReading {os.path.basename(state)}')
        text, q, event, restart = summary(state)
        print(text)
        if event:
            print('Note: this state was made during an event. The game never saves at such a moment,')
            print('so its story flags may be half-updated, and the save will restart at the restart')
            print('place rather than inside the event.')
        if input('Open it in BlueWake? [Y/n]: ').strip().lower() != 'n':
            print('Starting BlueWake; close it when you are done looking.')
            env = dict(os.environ, BLUEWAKE_LOAD_STATE=state)
            # BlueWake writes its own session log under user\\logs; keep this window readable.
            subprocess.run([exe], cwd=os.path.dirname(exe), env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print('BlueWake closed. (Its session log is in the build\'s user\\logs folder.)')
        if input('Catalog this state? [y/N]: ').strip().lower() == 'y':
            catalog(os.path.basename(state), q, text, event)


def check():
    states = sorted(glob.glob(os.path.join(STATES, '*.bwstate')), key=os.path.getmtime)
    print('\nWhich state did you load before saving in game?')
    state = states[pick('State: ', [os.path.basename(s) for s in states])]
    entries = sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci')))
    print('\nWhich catalog entry holds the save you made from it?')
    gci = entries[pick('Entry: ', [os.path.basename(os.path.dirname(e)) for e in entries])]
    slot = int(input('Quest log the game saved to [1]: ').strip() or '1')
    print()
    compare(state, gci, slot)


# Story flags from zeldaret/tww include/d/d_save_event_flag.inc
# (all names there are informal; UNK_ ones are left unnamed here).
FLAG_BITS = [
    (0x0080, '', ''),
    (0x0020, '', ''),
    (0x0010, '', ''),
    (0x0008, '', ''),
    (0x0004, '', ''),
    (0x0002, '', ''),
    (0x0001, '', ''),
    (0x0180, '', ''),
    (0x0140, '', ''),
    (0x0120, '', ''),
    (0x0108, '', ''),
    (0x0104, '', ''),
    (0x0102, '', ''),
    (0x0101, '', ''),
    (0x0280, '', ''),
    (0x0240, '', ''),
    (0x0220, '', ''),
    (0x0210, '', ''),
    (0x0208, '', ''),
    (0x0201, '', ''),
    (0x0380, '', ''),
    (0x0340, '', ''),
    (0x0310, '', ''),
    (0x0308, '', ''),
    (0x0304, '', ''),
    (0x0302, '', ''),
    (0x0301, '', ''),
    (0x0480, '', ''),
    (0x0420, '', ''),
    (0x0404, '', ''),
    (0x0402, '', ''),
    (0x0401, '', ''),
    (0x0580, '', ''),
    (0x0540, '', ''),
    (0x0520, '', ''),
    (0x0510, '', ''),
    (0x0508, '', ''),
    (0x0504, '', ''),
    (0x0502, '', ''),
    (0x0501, '', ''),
    (0x0640, '', ''),
    (0x0608, '', 'Set by an unused dialogue'),
    (0x0604, '', ''),
    (0x0602, '', 'Grandma dialogue after sword obtained'),
    (0x0601, '', 'Grandma dialogue after Helmaroc cutscene (prologue)'),
    (0x0780, '', ''),
    (0x0740, '', 'Grandma dialogue after Aryll kidnapped'),
    (0x0720, '', ''),
    (0x0710, '', ''),
    (0x0704, '', ''),
    (0x0702, '', ''),
    (0x0701, '', ''),
    (0x0880, '', ''),
    (0x0840, '', ''),
    (0x0820, '', ''),
    (0x0810, '', ''),
    (0x0808, '', ''),
    (0x0804, '', ''),
    (0x0802, '', ''),
    (0x0801, '', ''),
    (0x0940, '', ''),
    (0x0920, '', ''),
    (0x0910, '', ''),
    (0x0908, '', ''),
    (0x0904, '', ''),
    (0x0902, '', ''),
    (0x0901, '', ''),
    (0x0A80, '', ''),
    (0x0A40, '', ''),
    (0x0A20, '', ''),
    (0x0A10, '', ''),
    (0x0A08, '', ''),
    (0x0A04, '', ''),
    (0x0A02, 'ENDLESS_NIGHT', ''),
    (0x0A01, '', ''),
    (0x0B80, '', ''),
    (0x0B40, '', ''),
    (0x0B20, '', ''),
    (0x0B08, '', ''),
    (0x0B04, '', ''),
    (0x0B02, '', ''),
    (0x0B01, '', ''),
    (0x0C80, '', ''),
    (0x0C40, '', ''),
    (0x0C20, '', ''),
    (0x0C10, '', ''),
    (0x0C08, '', ''),
    (0x0C04, '', ''),
    (0x0C02, '', ''),
    (0x0D80, '', ''),
    (0x0D40, '', ''),
    (0x0D20, '', ''),
    (0x0D10, '', ''),
    (0x0D08, '', ''),
    (0x0D04, '', ''),
    (0x0D02, '', ''),
    (0x0E80, '', ''),
    (0x0E40, '', ''),
    (0x0E20, '', ''),
    (0x0E10, '', ''),
    (0x0E08, '', ''),
    (0x0E04, '', ''),
    (0x0E02, 'MEDLI_GAVE_FATHERS_LETTER', ''),
    (0x0E01, '', ''),
    (0x0F80, 'MET_KORL', ''),
    (0x0F40, '', ''),
    (0x0F20, '', ''),
    (0x0F10, '', ''),
    (0x0F08, '', ''),
    (0x0F04, '', ''),
    (0x0F02, '', ''),
    (0x0F01, '', ''),
    (0x1080, '', ''),
    (0x1040, '', ''),
    (0x1020, '', ''),
    (0x1010, '', ''),
    (0x1008, '', ''),
    (0x1004, '', ''),
    (0x1002, '', ''),
    (0x1001, '', 'Set by fairy.stb fairy_flag_on.stb (stage: sea)'),
    (0x1140, '', ''),
    (0x1120, '', ''),
    (0x1110, '', ''),
    (0x1108, '', ''),
    (0x1104, '', ''),
    (0x1102, '', ''),
    (0x1101, '', ''),
    (0x1280, '', ''),
    (0x1240, '', ''),
    (0x1220, '', ''),
    (0x1210, '', ''),
    (0x1208, '', ''),
    (0x1204, '', ''),
    (0x1202, '', ''),
    (0x1201, '', ''),
    (0x1380, '', ''),
    (0x1340, '', ''),
    (0x1320, '', ''),
    (0x1310, '', ''),
    (0x1308, '', ''),
    (0x1304, '', ''),
    (0x1302, '', ''),
    (0x1301, '', ''),
    (0x1480, 'PLACED_DINS_PEARL', ''),
    (0x1440, 'PLACED_FARORES_PEARL', ''),
    (0x1420, '', ''),
    (0x1410, 'PLACED_NAYRUS_PEARL', ''),
    (0x1408, '', ''),
    (0x1404, '', ''),
    (0x1402, '', ''),
    (0x1401, '', ''),
    (0x1580, '', ''),
    (0x1540, '', ''),
    (0x1520, '', ''),
    (0x1510, '', ''),
    (0x1508, '', ''),
    (0x1504, '', ''),
    (0x1502, '', ''),
    (0x1501, '', ''),
    (0x1680, '', ''),
    (0x1640, '', ''),
    (0x1620, '', ''),
    (0x1610, '', ''),
    (0x1608, '', ''),
    (0x1604, '', ''),
    (0x1602, '', ''),
    (0x1601, '', ''),
    (0x1780, '', ''),
    (0x1740, '', ''),
    (0x1720, '', ''),
    (0x1710, '', ''),
    (0x1708, '', ''),
    (0x1704, '', ''),
    (0x1701, '', ''),
    (0x1880, '', ''),
    (0x1840, '', ''),
    (0x1820, '', ''),
    (0x1810, '', ''),
    (0x1808, '', ''),
    (0x1804, '', ''),
    (0x1802, '', ''),
    (0x1801, '', ''),
    (0x1980, '', ''),
    (0x1940, '', ''),
    (0x1920, '', ''),
    (0x1910, '', ''),
    (0x1908, '', ''),
    (0x1904, '', ''),
    (0x1902, '', ''),
    (0x1901, '', ''),
    (0x1A80, '', ''),
    (0x1A20, '', ''),
    (0x1A10, 'UNLOCK_TINGLE_BALLOON_DISCOUNT', ''),
    (0x1A08, 'UNLOCK_TING_DISCOUNT', ''),
    (0x1A04, '', ''),
    (0x1A02, '', ''),
    (0x1A01, '', ''),
    (0x1B80, '', ''),
    (0x1B40, '', ''),
    (0x1B20, '', ''),
    (0x1B10, '', ''),
    (0x1B04, '', ''),
    (0x1B01, '', ''),
    (0x1C80, '', ''),
    (0x1C40, '', ''),
    (0x1C20, '', ''),
    (0x1C08, '', ''),
    (0x1C04, '', ''),
    (0x1C02, '', ''),
    (0x1C01, '', ''),
    (0x1D80, '', ''),
    (0x1D40, '', ''),
    (0x1D20, '', ''),
    (0x1D10, '', ''),
    (0x1D08, '', ''),
    (0x1D04, '', ''),
    (0x1D02, '', ''),
    (0x1D01, '', ''),
    (0x1E80, '', ''),
    (0x1E40, '', ''),
    (0x1E20, '', ''),
    (0x1E10, '', ''),
    (0x1E08, '', ''),
    (0x1E04, '', ''),
    (0x1E02, '', ''),
    (0x1E01, '', ''),
    (0x1F80, '', ''),
    (0x1F40, '', ''),
    (0x1F20, '', ''),
    (0x1F10, '', ''),
    (0x1F08, '', ''),
    (0x1F04, '', ''),
    (0x1F02, '', ''),
    (0x1F01, '', ''),
    (0x2080, '', ''),
    (0x2040, '', ''),
    (0x2020, '', ''),
    (0x2010, '', ''),
    (0x2008, '', ''),
    (0x2004, '', ''),
    (0x2002, '', ''),
    (0x2001, '', ''),
    (0x2180, '', ''),
    (0x2140, '', ''),
    (0x2120, '', ''),
    (0x2110, '', 'Set by bombshop.stb (stage: Obombh)'),
    (0x2108, '', ''),
    (0x2104, '', ''),
    (0x2102, '', ''),
    (0x2101, '', ''),
    (0x2280, '', ''),
    (0x2240, '', ''),
    (0x2220, '', ''),
    (0x2210, '', ''),
    (0x2208, '', ''),
    (0x2204, '', ''),
    (0x2202, '', ''),
    (0x2201, '', ''),
    (0x2340, '', ''),
    (0x2320, '', ''),
    (0x2310, '', ''),
    (0x2308, '', ''),
    (0x2304, '', ''),
    (0x2302, '', ''),
    (0x2301, '', ''),
    (0x2480, '', ''),
    (0x2440, '', ''),
    (0x2420, '', ''),
    (0x2410, '', ''),
    (0x2408, '', ''),
    (0x2404, '', ''),
    (0x2402, '', ''),
    (0x2401, '', 'Set by departure_DEMO.stb (stage: sea)'),
    (0x2580, '', 'Set by FIND_SISTER.stb (stage: Mjtower)'),
    (0x2540, '', ''),
    (0x2520, '', ''),
    (0x2510, '', ''),
    (0x2508, '', ''),
    (0x2504, '', ''),
    (0x2502, '', ''),
    (0x2501, '', ''),
    (0x2680, '', ''),
    (0x2640, '', ''),
    (0x2620, '', ''),
    (0x2608, '', ''),
    (0x2604, '', ''),
    (0x2602, '', ''),
    (0x2601, '', ''),
    (0x2780, '', ''),
    (0x2740, '', ''),
    (0x2710, '', ''),
    (0x2708, '', ''),
    (0x2704, '', ''),
    (0x2702, '', ''),
    (0x2701, '', ''),
    (0x2880, '', ''),
    (0x2840, '', ''),
    (0x2820, '', ''),
    (0x2810, '', ''),
    (0x2808, '', ''),
    (0x2804, '', ''),
    (0x2802, '', ''),
    (0x2801, '', ''),
    (0x2980, '', ''),
    (0x2940, '', ''),
    (0x2920, '', ''),
    (0x2910, '', ''),
    (0x2908, '', ''),
    (0x2904, '', ''),
    (0x2902, '', ''),
    (0x2901, '', ''),
    (0x2A80, '', ''),
    (0x2A40, '', ''),
    (0x2A20, 'GRANDMA_HEALED', ''),
    (0x2A10, '', ''),
    (0x2A08, 'RODE_KORL', ''),
    (0x2A04, '', ''),
    (0x2A02, '', ''),
    (0x2A01, '', ''),
    (0x2B80, '', ''),
    (0x2B40, '', ''),
    (0x2B20, '', ''),
    (0x2B10, '', 'Command melody monument in Tower of the Gods has been revealed'),
    (0x2B08, '', ''),
    (0x2B04, '', ''),
    (0x2C80, '', ''),
    (0x2C40, '', ''),
    (0x2C20, '', ''),
    (0x2C08, '', ''),
    (0x2C04, '', ''),
    (0x2C02, 'BARRIER_BREAK', ''),
    (0x2C01, '', ''),
    (0x2D80, '', ''),
    (0x2D40, '', 'Set by dance_zola.stb (stage: Edaichi)'),
    (0x2D20, '', 'Set by dance_kokiri.stb (stage: Ekaze)'),
    (0x2D10, '', 'Set by warp_in.stb (stage: ADMumi)'),
    (0x2D08, '', 'Set by warphole.stb (stage: ADMumi)'),
    (0x2D04, 'MASTER_SWORD_CUTSCENE', 'Set by master_sword.stb (stage: kenroom)'),
    (0x2D02, 'ZELDA_AWAKENED', 'Set by awake_zelda.stb (stage: kenroom)'),
    (0x2D01, '', 'Set by rescue.stb (stage: M2tower)'),
    (0x2E80, '', 'Set by towerd.stb, towerf.stb, towern.stb (stage: ADMumi)'),
    (0x2E40, '', ''),
    (0x2E20, '', ''),
    (0x2E10, '', ''),
    (0x2E08, '', ''),
    (0x2E04, '', ''),
    (0x2E02, '', ''),
    (0x2E01, '', 'Set by MEETSHISHIOH.stb (stage: sea)'),
    (0x2F80, '', ''),
    (0x2F40, '', ''),
    (0x2F20, '', ''),
    (0x2F10, '', ''),
    (0x2F08, '', ''),
    (0x2F04, '', ''),
    (0x2F02, '', ''),
    (0x2F01, '', ''),
    (0x3080, '', ''),
    (0x3040, '', ''),
    (0x3020, '', ''),
    (0x3010, '', ''),
    (0x3008, '', ''),
    (0x3004, '', ''),
    (0x3002, '', ''),
    (0x3001, '', ''),
    (0x3180, '', ''),
    (0x3140, '', ''),
    (0x3120, '', ''),
    (0x3104, '', ''),
    (0x3102, '', ''),
    (0x3101, '', ''),
    (0x3280, '', 'Set by runaway_majuto.stb (stage: ADMumi)'),
    (0x3240, 'GOHMA_TRIALS_CLEAR', ''),
    (0x3220, 'KALLE_DEMOS_TRIALS_CLEAR', ''),
    (0x3210, 'JALHALLA_TRIALS_CLEAR', ''),
    (0x3208, 'MOLGERA_TRIALS_CLEAR', ''),
    (0x3204, '', ''),
    (0x3202, '', ''),
    (0x3201, '', ''),
    (0x3380, '', ''),
    (0x3340, '', ''),
    (0x3320, '', ''),
    (0x3310, '', ''),
    (0x3308, '', ''),
    (0x3304, '', ''),
    (0x3302, '', ''),
    (0x3301, '', ''),
    (0x3480, '', ''),
    (0x3440, '', ''),
    (0x3420, '', ''),
    (0x3410, '', ''),
    (0x3408, '', ''),
    (0x3404, '', ''),
    (0x3402, '', ''),
    (0x3401, '', ''),
    (0x3580, '', ''),
    (0x3540, '', ''),
    (0x3520, '', ''),
    (0x3510, '', ''),
    (0x3508, 'LITHOGRAPH_1', ''),
    (0x3504, 'LITHOGRAPH_2', ''),
    (0x3502, 'LITHOGRAPH_3', ''),
    (0x3501, 'LITHOGRAPH_4', ''),
    (0x3680, 'LITHOGRAPH_5', ''),
    (0x3640, 'LITHOGRAPH_6', ''),
    (0x3620, 'LITHOGRAPH_7', ''),
    (0x3610, 'LITHOGRAPH_8', ''),
    (0x3608, 'LITHOGRAPH_9', ''),
    (0x3604, 'LITHOGRAPH_10', ''),
    (0x3602, '', ''),
    (0x3601, '', ''),
    (0x3780, '', ''),
    (0x3740, '', ''),
    (0x3720, '', ''),
    (0x3710, '', ''),
    (0x3708, '', ''),
    (0x3704, '', ''),
    (0x3702, '', ''),
    (0x3701, '', ''),
    (0x3880, '', ''),
    (0x3840, '', ''),
    (0x3820, 'MOVED_HYRULE_STATUE', ''),
    (0x3810, '', ''),
    (0x3808, '', ''),
    (0x3804, 'HYRULE_COURTYARD_CUTSCENE', ''),
    (0x3802, 'COLORS_IN_HYRULE', ''),
    (0x3801, '', ''),
    (0x3980, '', ''),
    (0x3940, '', ''),
    (0x3920, '', 'Set by getperl_jab.stb (stage: Pjavdou)'),
    (0x3910, '', 'Set by attack_ganon.stb (stage: M2ganon)'),
    (0x3908, '', ''),
    (0x3904, 'TRIALS_DOOR_LIGHT_GOHMA', ''),
    (0x3902, 'TRIALS_DOOR_LIGHT_KALLE_DEMOS', ''),
    (0x3901, 'TRIALS_DOOR_LIGHT_JALHALLA', ''),
    (0x3A80, 'TRIALS_DOOR_LIGHT_MOLGERA', ''),
    (0x3A40, '', ''),
    (0x3A20, '', ''),
    (0x3A10, '', ''),
    (0x3A08, '', ''),
    (0x3A04, 'MASTER_SWORD_SWINGING_CUTSCENE', 'Set by swing_sword.stb (stage: kenroom)'),
    (0x3A02, '', 'Set by pray_zola.stb (stage: M_DaiB)'),
    (0x3A01, '', ''),
    (0x3B80, '', ''),
    (0x3B40, '', ''),
    (0x3B20, '', ''),
    (0x3B10, '', 'Set by awake_zola.stb (stage: sea)'),
    (0x3B08, '', 'Set by seal.stb (stage: Hyrule)'),
    (0x3B04, '', ''),
    (0x3B02, '', 'Set by kugutu_ganon.stb (stage: GanonK)'),
    (0x3B01, '', ''),
    (0x3C80, '', ''),
    (0x3C40, '', ''),
    (0x3C20, '', ''),
    (0x3C10, '', ''),
    (0x3C08, '', ''),
    (0x3C04, '', ''),
    (0x3C02, '', ''),
    (0x3C01, '', ''),
    (0x3D80, '', ''),
    (0x3D40, '', ''),
    (0x3D20, '', ''),
    (0x3D10, '', ''),
    (0x3D08, '', ''),
    (0x3D04, '', ''),
    (0x3D02, '', ''),
    (0x3D01, '', ''),
    (0x3E80, '', ''),
    (0x3E40, '', ''),
    (0x3E20, '', ''),
    (0x3E10, '', ''),
    (0x3E04, '', ''),
    (0x3E02, '', ''),
    (0x3E01, '', ''),
    (0x3F80, '', ''),
    (0x3F40, '', 'Set by endhr.stb (stage: GTower)'),
    (0x3F20, '', ''),
    (0x3F10, '', ''),
    (0x3F02, '', ''),
    (0x3F01, '', ''),
    (0x4080, '', ''),
    (0x4040, '', ''),
    (0x4020, '', ''),
    (0x4008, '', ''),
    (0x4004, '', 'Set by pray_kokiri.stb (stage: kazeB)'),
    (0x4002, '', 'Set by g2before.stb (stage: GTower)'),
    (0x4001, '', ''),
    (0x4180, '', '')
]
FLAG_REGS = [
    (0x790F, '', ''),
    (0x7A03, 'LETTER_ROCK_SPIRE_SHOP_AD', ''),
    (0x7B03, 'LETTER_ORCA', ''),
    (0x7C03, 'LETTER_BAITO', ''),
    (0x7D03, 'LETTER_BOMBS_AD', ''),
    (0x7EFF, '', ''),
    (0x7F0F, '', ''),
    (0x80FF, '', ''),
    (0x81FF, '', ''),
    (0x82FF, '', ''),
    (0x83FF, '', ''),
    (0x84FF, '', ''),
    (0x85FF, '', ''),
    (0x86FF, '', ''),
    (0x870F, '', ''),
    (0x8803, 'GHOST_SHIP', ''),
    (0x89FF, '', ''),
    (0x8AFF, '', ''),
    (0x8B03, 'LETTER_ARYLL', ''),
    (0x8CFF, '', ''),
    (0x8DFF, '', ''),
    (0x8EFF, '', ''),
    (0x8FFF, '', ''),
    (0x90FF, '', ''),
    (0x91FF, '', ''),
    (0x92FF, '', ''),
    (0x93FF, '', ''),
    (0x94FF, '', ''),
    (0x95FF, '', ''),
    (0x96FF, '', ''),
    (0x97FF, '', ''),
    (0x98FF, '', ''),
    (0x99FF, '', ''),
    (0x9AFF, '', ''),
    (0x9B07, '', ''),
    (0x9CFF, '', ''),
    (0x9D03, 'LETTER_GRANDMA', ''),
    (0x9EFF, '', ''),
    (0x9F07, '', ''),
    (0xA007, '', ''),
    (0xA107, '', ''),
    (0xA207, '', ''),
    (0xA307, '', ''),
    (0xA407, '', ''),
    (0xA507, '', ''),
    (0xA60F, '', ''),
    (0xA7FF, '', ''),
    (0xA8FF, '', ''),
    (0xA9FF, '', ''),
    (0xAAFF, '', ''),
    (0xAB03, '', ''),
    (0xAC03, 'LETTER_BAITOS_MOM', ''),
    (0xADFF, '', ''),
    (0xAE03, 'LETTER_HOSKITS_GIRLFRIEND', ''),
    (0xAF03, 'LETTER_GOLD_MEMBERSHIP', ''),
    (0xB003, 'LETTER_SILVER_MEMBERSHIP', ''),
    (0xB1FF, '', ''),
    (0xB203, 'LETTER_TINGLE', ''),
    (0xB503, 'LETTER_KOMALIS_FATHER', ''),
    (0xB6FF, '', ''),
    (0xB703, '', ''),
    (0xB8FF, '', ''),
    (0xB907, '', ''),
    (0xBA0F, '', ''),
    (0xBB07, '', ''),
    (0xBCFF, '', ''),
    (0xBEFF, '', ''),
    (0xBFFF, '', ''),
    (0xC0FF, '', ''),
    (0xC103, '', ''),
    (0xC203, '', ''),
    (0xC3FF, '', ''),
    (0xC407, '', ''),
    (0xC5FF, '', ''),
    (0xC603, '', 'Unused?'),
    (0xC703, '', 'Unused?'),
    (0xC803, '', 'Unused?'),
    (0xC903, '', ''),
    (0xCA03, '', ''),
    (0xCB03, '', ''),
    (0xCCFF, '', ''),
    (0xCD03, '', ''),
    (0xCF03, '', ''),
    (0xD003, '', ''),
    (0xD1FF, '', ''),
    (0xD2FF, '', ''),
    (0xD3FF, '', ''),
    (0xD4FF, '', ''),
    (0xD5FF, '', ''),
    (0xD6FF, '', ''),
    (0xD7FF, '', ''),
    (0xD8FF, '', ''),
    (0xD9FF, '', ''),
    (0xDAFF, '', ''),
    (0xDBFF, '', ''),
    (0xDCFF, '', ''),
    (0xDDFF, '', ''),
    (0xDEFF, '', ''),
    (0xDFFF, '', ''),
    (0xE0FF, '', ''),
    (0xE1FF, '', ''),
    (0xE2FF, '', ''),
    (0xE3FF, '', ''),
    (0xE4FF, '', ''),
    (0xE5FF, '', ''),
    (0xE6FF, '', ''),
    (0xE7FF, '', ''),
    (0xE8FF, '', ''),
    (0xE9FF, '', ''),
    (0xEAFF, '', ''),
    (0xEBFF, '', ''),
    (0xECFF, '', ''),
    (0xEDFF, '', ''),
    (0xEEFF, '', ''),
    (0xEFFF, '', ''),
    (0xF0FF, '', ''),
    (0xF1FF, '', ''),
    (0xF2FF, '', ''),
    (0xF3FF, '', ''),
    (0xF4FF, '', ''),
    (0xF5FF, '', ''),
    (0xF6FF, '', ''),
    (0xF7FF, '', ''),
    (0xF8FF, '', ''),
    (0xF903, '', ''),
    (0xFAFF, '', ''),
    (0xFBFF, '', ''),
    (0xFC03, '', ''),
    (0xFD07, '', ''),
    (0xFE07, '', ''),
    (0xFF07, '', '')
]



# Notes from the Wind Waker Randomizer's patches (github.com/LagoLunatic/wwrando, asm/patches).
WWRANDO_NOTES = {
    0x0280: 'SAW_TETRA_IN_FOREST_OF_FAIRIES',
    0x0310: "Saw event where Grandma gives you the Hero's Clothes",
    0x0520: 'GOSSIP_STONE_AT_FF1 (Causes Aryll and the pirates to disappear from Outset)',
    0x0808: 'Needed so that exiting the pirate ship takes you to Windfall instead of the tutorial',
    0x0901: 'TRIGGERED_MAP_FISH',
    0x0902: 'SAW_DRAGON_ROOST_ISLAND_INTRO',
    0x0908: 'SAIL_INTRODUCTION_TEXT_AND_MAP_UNLOCKED',
    0x0A08: 'TALKED_TO_KORL_AFTER_LEAVING_FH',
    0x0A20: 'WATCHED_FOREST_HAVEN_INTRO_CUTSCENE',
    0x0A80: 'KORL_DINS_PEARL_TEXT_ALLOWING_YOU_TO_ENTER_HIM',
    0x0F80: 'KORL_UNLOCKED_AND_SPAWN_ON_WINDFALL',
    0x1001: 'WATCHED_FIRE_AND_ICE_ARROWS_CUTSCENE',
    0x1410: "Placed Nayru's Pearl",
    0x1440: "Placed Farore's Pearl",
    0x1480: "Placed Din's Pearl",
    0x1610: 'Makar is in dungeon mode and can be lifted/called',
    0x1620: 'Medli is in dungeon mode and can be lifted/called',
    0x1801: 'WATCHED_DEKU_TREE_CUTSCENE',
    0x1E40: 'TOWER_OF_THE_GODS_RAISED',
    0x1F02: 'TALKED_TO_KORL_AFTER_GETTING_BOMBS',
    0x1F40: 'SAW_QUILL_CUTSCENE_ON_DRI',
    0x2510: 'Learned Command Melody from the TotG stone tablet',
    0x2910: 'MAKAR_IN_WIND_TEMPLE',
    0x2920: 'MEDLI_IN_EARTH_TEMPLE',
    0x2A08: 'ENTER_KORL_FOR_THE_FIRST_TIME_AND_SPAWN_ANYWHERE',
    0x2A80: "HAS_HEROS_CLOTHES (This should be set even if the player wants to wear casual clothes, it's overridden elsewhere)",
    0x2C02: 'BARRIER_DOWN',
    0x2D01: 'ANIMATION_SET_2 (Saw cutscene before Helmaroc King where Aryll is rescued)',
    0x2D02: 'TETRA_TO_ZELDA_CUTSCENE',
    0x2D04: 'MASTER_SWORD_CUTSCENE',
    0x2D08: 'HYRULE_3_WARP_CUTSCENE',
    0x2E01: 'WATCHED_MEETING_KORL_CUTSCENE (Necessary for Windfall music to play when warping there)',
    0x2E04: 'MEDLI_IN_EARTH_TEMPLE_ENTRANCE',
    0x2E80: 'PEARL_TOWER_CUTSCENE',
    0x2F20: "Talked to KoRL after getting Nayru's Pearl",
    0x3201: 'KoRL told you about the sages',
    0x3304: 'Saw event where Medli calls to you from within jail',
    0x3380: 'KoRL told you about the Triforce shards',
    0x3440: 'Saw event where Makar calls to you from within jail',
    0x3510: 'HAS_SEEN_INTRO',
    0x3802: 'COLORS_IN_HYRULE',
    0x3840: 'TALKED_TO_KORL_POST_TOWER_CUTSCENE',
    0x3901: 'Recollection Jalhalla defeated',
    0x3902: 'Recollection Kalle Demos defeated',
    0x3904: 'Recollection Gohma defeated',
    0x3980: 'HYRULE_3_ELECTRICAL_BARRIER_CUTSCENE_1',
    0x3A20: 'Fishman and KoRL talked about Forsaken Fortress after you beat Molgera',
    0x3A80: 'Recollection Molgera defeated',
    0x3B02: 'Saw cutscene before Puppet Ganon fight',
    0x3B08: 'Another event flag set by the barrier. This one seems to have no effect, but set it anyway just to be safe.',
    0x3D04: 'Saw the Triforce refuse',
    0x4002: 'Saw cutscene before Ganondorf fight',
}

# The ZeldaSpeedRuns community flag spreadsheet (linked from
# zeldaspeedruns.com/tww/general-knowledge/flags-and-triggers): a description for
# nearly every story bit. Downloaded once and kept next to the catalog.
SHEET_URL = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vRpX8gq6LK1wt0OL7eqSNE-F10XEQ0lOWXxZsy_'
             'krB9ejPza8wGUZMDAMLMVCtO2akXfKpSMqc5M2Zy/pub?output=csv')
SHEET_CACHE = os.path.join(config.ROOT, 'zsr-event-flags.csv')
SHEET = None


def load_sheet(refresh=False):
    """Return {flag: description} from the ZeldaSpeedRuns sheet, downloading it if needed."""
    import csv
    import re
    import urllib.request
    global SHEET
    if SHEET is not None and not refresh:
        return SHEET
    if refresh or not os.path.isfile(SHEET_CACHE):
        print('Downloading the ZeldaSpeedRuns flag spreadsheet...')
        try:
            data = urllib.request.urlopen(SHEET_URL, timeout=30).read()
            os.makedirs(os.path.dirname(SHEET_CACHE), exist_ok=True)
            open(SHEET_CACHE, 'wb').write(data)
            print(f'Saved a copy to {SHEET_CACHE}')
        except Exception as error:
            print(f'Could not download it ({error}); continuing without its descriptions.')
    SHEET = {}
    if os.path.isfile(SHEET_CACHE):
        with open(SHEET_CACHE, encoding='utf-8', newline='') as f:
            for row in csv.reader(f):
                m = re.search(r'\(0x([0-9A-Fa-f]+)\)', row[0] if row else '')
                if not m:
                    continue
                byte = int(m.group(1), 16)
                for i, cell in enumerate(row[1:9]):
                    if cell.strip():
                        SHEET[byte << 8 | 0x80 >> i] = ' '.join(cell.split())
    return SHEET


def describe_flag(v, name='', comment=''):
    """Best available description of a story bit or counter, from every source."""
    parts = []
    sheet = load_sheet().get(v)
    if sheet:
        parts.append(sheet)
    if v in WWRANDO_NOTES and (not sheet or WWRANDO_NOTES[v].lower() not in sheet.lower()):
        parts.append(f'rando: {WWRANDO_NOTES[v]}')
    if name and not any(name in p for p in parts):
        parts.append(f'decomp: {name}')
    if comment:
        parts.append(f'decomp: {comment}')
    return '; '.join(parts)

# ---- Story flag comparison ------------------------------------------------

REG_MASKS = {}                    # byte index -> list of (mask, value, name, comment)
for v, n, c in FLAG_REGS:
    REG_MASKS.setdefault(v >> 8, []).append((v & 0xFF, v, n, c))
BIT_INFO = {v: (n, c) for v, n, c in FLAG_BITS}


def flag_label(v, name, comment):
    about = describe_flag(v, name, comment)
    return f'0x{v:04X}' + (f'  {about}' if about else '')


def entry_quest(gci):
    d = open(gci, 'rb').read()
    return d[HEADER + BLOCK + 8:][:QUEST]


def save_time(q):
    ticks = struct.unpack('>Q', q[0x18:0x20])[0]
    return ticks / 40500000 if ticks else float('inf')


def flag_changes(a, b):
    """Story flag differences between two card quest logs (packed layout)."""
    out = []
    fa, fb = a[0x618:0x718], b[0x618:0x718]
    for i in range(0x100):
        if fa[i] == fb[i]:
            continue
        reg_bits = 0
        for mask, v, n, c in REG_MASKS.get(i, []):
            reg_bits |= mask
            if fa[i] & mask != fb[i] & mask:
                shift = (mask & -mask).bit_length() - 1
                out.append(f'  ~ {flag_label(v, n, c)}: {(fa[i] & mask) >> shift} -> {(fb[i] & mask) >> shift}')
        for bit in range(8):
            m = 1 << bit
            if reg_bits & m or (fa[i] & m) == (fb[i] & m):
                continue
            v = i << 8 | m
            n, c = BIT_INFO.get(v, ('', ''))
            out.append(f'  {"+" if fb[i] & m else "-"} {flag_label(v, n, c)}')
    return out



# Item names by item ID, from the Wind Waker Randomizer (data/item_names.txt).
ITEM_NAMES = {
    0x00: 'Heart (Pickup)',
    0x01: 'Green Rupee',
    0x02: 'Blue Rupee',
    0x03: 'Yellow Rupee',
    0x04: 'Red Rupee',
    0x05: 'Purple Rupee',
    0x06: 'Orange Rupee',
    0x07: 'Piece of Heart',
    0x08: 'Heart Container',
    0x09: 'Small Magic Jar (Pickup)',
    0x0A: 'Large Magic Jar (Pickup)',
    0x0B: '5 Bombs (Pickup)',
    0x0C: '10 Bombs (Pickup)',
    0x0D: '20 Bombs (Pickup)',
    0x0E: '30 Bombs (Pickup)',
    0x0F: 'Silver Rupee',
    0x10: '10 Arrows (Pickup)',
    0x11: '20 Arrows (Pickup)',
    0x12: '30 Arrows (Pickup)',
    0x15: 'Small Key',
    0x16: 'Fairy (Pickup)',
    0x1A: 'Yellow Rupee (Joke Message)',
    0x1E: 'Three Hearts (Pickup)',
    0x1F: 'Joy Pendant',
    0x20: 'Telescope',
    0x21: 'Tingle Tuner',
    0x22: 'Wind Waker',
    0x23: 'Picto Box',
    0x24: 'Spoils Bag',
    0x25: 'Grappling Hook',
    0x26: 'Deluxe Picto Box',
    0x27: "Hero's Bow",
    0x28: 'Power Bracelets',
    0x29: 'Iron Boots',
    0x2A: 'Magic Armor',
    0x2C: 'Bait Bag',
    0x2D: 'Boomerang',
    0x2F: 'Hookshot',
    0x30: 'Delivery Bag',
    0x31: 'Bombs',
    0x32: "Hero's Clothes",
    0x33: 'Skull Hammer',
    0x34: 'Deku Leaf',
    0x35: 'Fire and Ice Arrows',
    0x36: 'Light Arrow',
    0x37: "Hero's New Clothes",
    0x38: "Hero's Sword",
    0x39: 'Master Sword (Powerless)',
    0x3A: 'Master Sword (Half Power)',
    0x3B: "Hero's Shield",
    0x3C: 'Mirror Shield',
    0x3D: "Recovered Hero's Sword",
    0x3E: 'Master Sword (Full Power)',
    0x3F: 'Piece of Heart (Alternate Message)',
    0x42: "Pirate's Charm",
    0x43: "Hero's Charm",
    0x45: 'Skull Necklace',
    0x46: 'Boko Baba Seed',
    0x47: 'Golden Feather',
    0x48: "Knight's Crest",
    0x49: 'Red Chu Jelly',
    0x4A: 'Green Chu Jelly',
    0x4B: 'Blue Chu Jelly',
    0x4C: 'Dungeon Map',
    0x4D: 'Compass',
    0x4E: 'Big Key',
    0x50: 'Empty Bottle',
    0x51: 'Red Potion',
    0x52: 'Green Potion',
    0x53: 'Blue Potion',
    0x54: 'Elixir Soup (1/2)',
    0x55: 'Elixir Soup',
    0x56: 'Bottled Water',
    0x57: 'Fairy in Bottle',
    0x58: 'Forest Firefly',
    0x59: 'Forest Water',
    0x61: 'Triforce Shard 1',
    0x62: 'Triforce Shard 2',
    0x63: 'Triforce Shard 3',
    0x64: 'Triforce Shard 4',
    0x65: 'Triforce Shard 5',
    0x66: 'Triforce Shard 6',
    0x67: 'Triforce Shard 7',
    0x68: 'Triforce Shard 8',
    0x69: "Nayru's Pearl",
    0x6A: "Din's Pearl",
    0x6B: "Farore's Pearl",
    0x6D: "Wind's Requiem",
    0x6E: 'Ballad of Gales',
    0x6F: 'Command Melody',
    0x70: "Earth God's Lyric",
    0x71: "Wind God's Aria",
    0x72: 'Song of Passing',
    0x78: "Boat's Sail",
    0x79: 'Triforce Chart 1 got deciphered',
    0x7A: 'Triforce Chart 2 got deciphered',
    0x7B: 'Triforce Chart 3 got deciphered',
    0x7C: 'Triforce Chart 4 got deciphered',
    0x7D: 'Triforce Chart 5 got deciphered',
    0x7E: 'Triforce Chart 6 got deciphered',
    0x7F: 'Triforce Chart 7 got deciphered',
    0x80: 'Triforce Chart 8 got deciphered',
    0x82: 'All-Purpose Bait',
    0x83: 'Hyoi Pear',
    0x8C: 'Town Flower',
    0x8D: 'Sea Flower',
    0x8E: 'Exotic Flower',
    0x8F: "Hero's Flag",
    0x90: 'Big Catch Flag',
    0x91: 'Big Sale Flag',
    0x92: 'Pinwheel',
    0x93: 'Sickle Moon Flag',
    0x94: 'Skull Tower Idol',
    0x95: 'Fountain Idol',
    0x96: 'Postman Statue',
    0x97: 'Shop Guru Statue',
    0x98: "Father's Letter",
    0x99: 'Note to Mom',
    0x9A: "Maggie's Letter",
    0x9B: "Moblin's Letter",
    0x9C: 'Cabana Deed',
    0x9D: 'Complimentary ID',
    0x9E: 'Fill-Up Coupon',
    0x9F: 'Legendary Pictograph',
    0xA3: 'Dragon Tingle Statue',
    0xA4: 'Forbidden Tingle Statue',
    0xA5: 'Goddess Tingle Statue',
    0xA6: 'Earth Tingle Statue',
    0xA7: 'Wind Tingle Statue',
    0xAA: 'Hurricane Spin',
    0xAB: '1000 Rupee Wallet',
    0xAC: '5000 Rupee Wallet',
    0xAD: '60 Bomb Bomb Bag',
    0xAE: '99 Bomb Bomb Bag',
    0xAF: '60 Arrow Quiver',
    0xB0: '99 Arrow Quiver',
    0xB1: 'Magic Meter',
    0xB2: 'Magic Meter Upgrade',
    0xB3: '50 Rupees, reward for finding 1 Tingle Statue',
    0xB4: '100 Rupees, reward for finding 2 Tingle Statues',
    0xB5: '150 Rupees, reward for finding 3 Tingle Statues',
    0xB6: '200 Rupees, reward for finding 4 Tingle Statues',
    0xB7: '250 Rupees, reward for finding 5 Tingle Statues',
    0xB8: '500 Rupees, reward for finding all Tingle Statues',
    0xC2: 'Submarine Chart',
    0xC3: "Beedle's Chart",
    0xC4: 'Platform Chart',
    0xC5: 'Light Ring Chart',
    0xC6: 'Secret Cave Chart',
    0xC7: 'Sea Hearts Chart',
    0xC8: 'Island Hearts Chart',
    0xC9: 'Great Fairy Chart',
    0xCA: 'Octo Chart',
    0xCB: 'IN-credible Chart',
    0xCC: 'Treasure Chart 7',
    0xCD: 'Treasure Chart 27',
    0xCE: 'Treasure Chart 21',
    0xCF: 'Treasure Chart 13',
    0xD0: 'Treasure Chart 32',
    0xD1: 'Treasure Chart 19',
    0xD2: 'Treasure Chart 41',
    0xD3: 'Treasure Chart 26',
    0xD4: 'Treasure Chart 8',
    0xD5: 'Treasure Chart 37',
    0xD6: 'Treasure Chart 25',
    0xD7: 'Treasure Chart 17',
    0xD8: 'Treasure Chart 36',
    0xD9: 'Treasure Chart 22',
    0xDA: 'Treasure Chart 9',
    0xDB: 'Ghost Ship Chart',
    0xDC: "Tingle's Chart",
    0xDD: 'Treasure Chart 14',
    0xDE: 'Treasure Chart 10',
    0xDF: 'Treasure Chart 40',
    0xE0: 'Treasure Chart 3',
    0xE1: 'Treasure Chart 4',
    0xE2: 'Treasure Chart 28',
    0xE3: 'Treasure Chart 16',
    0xE4: 'Treasure Chart 18',
    0xE5: 'Treasure Chart 34',
    0xE6: 'Treasure Chart 29',
    0xE7: 'Treasure Chart 1',
    0xE8: 'Treasure Chart 35',
    0xE9: 'Treasure Chart 12',
    0xEA: 'Treasure Chart 6',
    0xEB: 'Treasure Chart 24',
    0xEC: 'Treasure Chart 39',
    0xED: 'Treasure Chart 38',
    0xEE: 'Treasure Chart 2',
    0xEF: 'Treasure Chart 33',
    0xF0: 'Treasure Chart 31',
    0xF1: 'Treasure Chart 23',
    0xF2: 'Treasure Chart 5',
    0xF3: 'Treasure Chart 20',
    0xF4: 'Treasure Chart 30',
    0xF5: 'Treasure Chart 15',
    0xF6: 'Treasure Chart 11',
    0xF7: 'Triforce Chart 8',
    0xF8: 'Triforce Chart 7',
    0xF9: 'Triforce Chart 6',
    0xFA: 'Triforce Chart 5',
    0xFB: 'Triforce Chart 4',
    0xFC: 'Triforce Chart 3',
    0xFD: 'Triforce Chart 2',
    0xFE: 'Triforce Chart 1',
}


def item_name(i):
    return 'nothing' if i == 0xFF else ITEM_NAMES.get(i, f'item 0x{i:02X}')


def bits_names(byte, names):
    return [n for i, n in enumerate(names) if byte & (1 << i)]


def inventory_changes(a, b):
    """Item, equipment and progress differences between two card quest logs."""
    out = []
    for i, part in enumerate(('sword', 'shield', 'bracelet', 'equipment slot 4')):
        x, y = a[0x0E + i], b[0x0E + i]
        if x != y:
            out.append(f'  * {part}: {item_name(x)} -> {item_name(y)}')
    for slot in range(21):
        x, y = a[0x3C + slot], b[0x3C + slot]
        if x != y:
            out.append(f'  * inventory slot {slot}: {item_name(x)} -> {item_name(y)}')
    for slot in range(24):
        x, y = a[0x76 + slot], b[0x76 + slot]
        if x != y:
            out.append(f'  * bag slot {slot}: {item_name(x)} -> {item_name(y)}')
    for off, what in ((0x00, 'max hearts'), (0x02, 'hearts')):
        x, y = struct.unpack('>H', a[off:off + 2])[0], struct.unpack('>H', b[off:off + 2])[0]
        if x != y and off == 0:
            out.append(f'  * {what}: {x / 4:g} -> {y / 4:g}')
    for off, what in ((0x12, 'wallet size'), (0x13, 'max magic')):
        if a[off] != b[off]:
            out.append(f'  * {what}: {a[off]} -> {b[off]}')
    songs = ["Wind's Requiem", 'Ballad of Gales', 'Command Melody', "Earth God's Lyric",
             "Wind God's Aria", 'Song of Passing', 'song 7', 'song 8']
    pearls = ["Nayru's Pearl", "Din's Pearl", "Farore's Pearl", 'pearl 4', 'pearl 5', 'pearl 6', 'pearl 7', 'pearl 8']
    for off, what, labels in ((0xB2 + 9, 'songs', songs), (0xB2 + 11, 'pearls', pearls)):
        new = set(bits_names(b[off], labels)) - set(bits_names(a[off], labels))
        if new:
            out.append(f'  * {what}: + ' + ', '.join(sorted(new)))
    if a[0xB2 + 10] != b[0xB2 + 10]:
        out.append(f'  * Triforce shards: {bin(a[0xB2 + 10]).count("1")} -> {bin(b[0xB2 + 10]).count("1")}')
    return out

def flags_timeline():
    entries = []
    for gci in glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci')):
        q = entry_quest(gci)
        entries.append((save_time(q), os.path.basename(os.path.dirname(gci)), q))
    entries.sort()
    if len(entries) < 2:
        print('Catalog at least two saves first.')
        return
    lines = [f'Story flag timeline: {len(entries)} saves, in the order they were made in the game',
             'Descriptions: ZeldaSpeedRuns flag spreadsheet, Wind Waker Randomizer notes (rando:),',
             'zeldaret/tww decomp names and cutscene notes (decomp:).', '']
    for (_, name_a, a), (_, name_b, b) in zip(entries, entries[1:]):
        changes = inventory_changes(a, b) + flag_changes(a, b)
        warn = ''
        if a[0x157:0x168] != b[0x157:0x168] or a[0x19B] != b[0x19B]:
            warn = '  [different player name or clear count: probably a different playthrough]'
        lines.append(f'{name_a}  ->  {name_b}: {len(changes)} change(s){warn}')
        lines += changes or ['  (no story flag changes)']
        lines.append('')
    report = os.path.join(CATALOG, 'flag-timeline.txt')
    with open(report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('\n'.join(lines))
    print(f'Also written to {report}')
    print('* items and progress, + flag turned on, - flag turned off, ~ a counter or value changed.')


def flags_pair():
    gcis = sorted(glob.glob(os.path.join(CATALOG, '*', 'GZLE01-gczelda.gci')))
    names = [os.path.basename(os.path.dirname(g)) for g in gcis]
    print('\nFirst save:')
    a = gcis[pick('Entry: ', names)]
    print('\nSecond save:')
    b = gcis[pick('Entry: ', names)]
    qa, qb = entry_quest(a), entry_quest(b)
    changes = inventory_changes(qa, qb) + flag_changes(qa, qb)
    print(f'\n{len(changes)} change(s):')
    print('\n'.join(changes) or '  (no story flag changes)')
    print('* items and progress, + flag turned on, - flag turned off, ~ a counter or value changed.')


def main():
    while True:
        print()
        i = pick('What do you want to do (q to quit)? ', [
            'Browse states, view them in BlueWake and catalog them',
            'Check the extraction against a save the game made',
            'Story flag timeline: what changed between each save, in story order',
            'Compare the story flags of two saves',
            'Re-download the ZeldaSpeedRuns flag spreadsheet'], allow_quit=True)
        if i is None:
            return
        [browse, check, flags_timeline, flags_pair, lambda: load_sheet(refresh=True)][i]()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
