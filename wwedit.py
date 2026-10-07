"""Wind Waker (GZLE01) save editing: the shared core for the craft tool and the GUI.

Works on Dolphin-style .gci files of the game's save (as card_to_gci.py and the catalog
write them). A .gci holds three quest logs, each stored twice; edits go to both copies
and every checksum is recomputed. Offsets are the packed card layout from the
zeldaret/tww decomp (dSv_save_c_PACKED); item behaviour copies d_item.cpp's item_func_*.
"""
import struct

BLOCK, QUEST, DATA, HEADER = 0x2000, 0x770, 0x768, 64

# Card quest log offsets
LIFE_MAX, LIFE, RUPEES = 0x00, 0x02, 0x04
EQUIP = 0x0E                       # sword, shield, bracelet, slot 4 (item IDs)
WALLET, MAGIC_MAX, MAGIC = 0x12, 0x13, 0x14
RESTART = 0x30                     # stage[8], room s8, point u8
ITEMS, GOT_ITEMS = 0x3C, 0x51      # 21 inventory slots; per-slot "obtained" bits
ARROWS, BOMBS = 0x69, 0x6A
ARROWS_MAX, BOMBS_MAX = 0x6F, 0x70
FLAGS = 0x618                      # story flags, 0x100 bytes

# name: (inventory slot, obtained bit, item ID, extra writes) from d_item.cpp
ITEMS_GIVEN = {
    'Telescope': (0, 0, 0x20, {}),
    "Boat's Sail": (1, 0, 0x78, {}),
    'Wind Waker': (2, 0, 0x22, {}),
    'Grappling Hook': (3, 0, 0x25, {}),
    'Spoils Bag': (4, 0, 0x24, {}),
    'Boomerang': (5, 0, 0x2D, {}),
    'Deku Leaf': (6, 0, 0x34, {MAGIC_MAX: 16, MAGIC: 16}),
    'Tingle Tuner': (7, 0, 0x21, {}),
    'Picto Box': (8, 0, 0x23, {}),
    'Deluxe Picto Box': (8, 1, 0x26, {}),
    'Iron Boots': (9, 0, 0x29, {}),
    'Magic Armor': (10, 0, 0x2A, {}),
    'Bait Bag': (11, 0, 0x2C, {}),
    "Hero's Bow": (12, 0, 0x27, {ARROWS: 30, ARROWS_MAX: 30}),
    'Fire and Ice Arrows': (12, 1, 0x35, {}),
    'Light Arrows': (12, 2, 0x36, {}),
    'Bombs': (13, 0, 0x31, {BOMBS: 30, BOMBS_MAX: 30}),
    'Delivery Bag': (18, 0, 0x30, {}),
    'Hookshot': (19, 0, 0x2F, {}),
    'Skull Hammer': (20, 0, 0x33, {}),
}
COLLECT = 0xB2                     # mCollect[8]: sword, shield, bracelet bits; then songs, shards, pearls
SONGS, SHARDS, PEARLS = 0xBB, 0xBC, 0xBD
SONG_NAMES = ["Wind's Requiem", 'Ballad of Gales', 'Command Melody', "Earth God's Lyric",
              "Wind God's Aria", 'Song of Passing']
PEARL_NAMES = ["Nayru's Pearl", "Din's Pearl", "Farore's Pearl"]
# Equipment: (name, item ID, collect bit) from item_func_sword / _shield / _pwr_groove
SWORDS = [('none', 0xFF, None), ("Hero's Sword", 0x38, 0), ('Master Sword (Powerless)', 0x39, 1),
          ('Master Sword (Half Power)', 0x3A, 2), ('Master Sword (Full Power)', 0x3E, 3)]
SHIELDS = [('none', 0xFF, None), ("Hero's Shield", 0x3B, 0), ('Mirror Shield', 0x3C, 1)]
BRACELETS = [('none', 0xFF, None), ('Power Bracelets', 0x28, 0)]
EQUIPMENT = [('Sword', SWORDS), ('Shield', SHIELDS), ('Bracelets', BRACELETS)]

SLOT_NAMES = ['Telescope', 'Sail', 'Wind Waker', 'Grappling Hook', 'Spoils Bag', 'Boomerang',
              'Deku Leaf', 'Tingle Tuner', 'Picto Box', 'Iron Boots', 'Magic Armor', 'Bait Bag',
              'Bow', 'Bombs', 'Bottle 1', 'Bottle 2', 'Bottle 3', 'Bottle 4', 'Delivery Bag',
              'Hookshot', 'Skull Hammer']


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


class Save:
    """One .gci; edits apply to one quest log (both copies) and are written with save()."""

    def __init__(self, path, slot=1):
        self.data = bytearray(open(path, 'rb').read())
        if self.data[0:4] != b'GZLE':
            raise ValueError('not a Wind Waker USA (GZLE) save')
        self.slot = slot
        self.q = bytearray(self._quest(0))

    def _offset(self, copy):
        return HEADER + BLOCK * (1 + copy) + 8 + (self.slot - 1) * QUEST

    def _quest(self, copy):
        o = self._offset(copy)
        return self.data[o:o + QUEST]

    def checksum_ok(self):
        return all(struct.unpack('>Q', q[DATA:DATA + 8])[0] == qsum(q)
                   for q in (self._quest(0), self._quest(1)))

    # -- reading
    def u16(self, off):
        return struct.unpack('>H', self.q[off:off + 2])[0]

    def name(self):
        return self.q[0x157:0x168].split(b'\0')[0].decode('latin-1')

    def restart(self):
        return (self.q[RESTART:RESTART + 8].split(b'\0')[0].decode('ascii', 'replace'),
                struct.unpack('b', self.q[RESTART + 8:RESTART + 9])[0], self.q[RESTART + 9])

    def flag(self, v):
        return bool(self.q[FLAGS + (v >> 8)] & (v & 0xFF))

    def has(self, item):
        slot, bit, item_id, _ = ITEMS_GIVEN[item]
        return self.q[ITEMS + slot] == item_id and bool(self.q[GOT_ITEMS + slot] & (1 << bit))

    # -- editing
    def set_u16(self, off, value):
        self.q[off:off + 2] = struct.pack('>H', value)

    def set_hearts(self, max_hearts, hearts=None):
        """Hearts in quarters, as the game stores them (4 = one heart)."""
        self.set_u16(LIFE_MAX, round(max_hearts * 4))
        self.set_u16(LIFE, round((hearts if hearts is not None else max_hearts) * 4))

    def set_rupees(self, n):
        self.set_u16(RUPEES, n)

    def set_wallet(self, size):
        self.q[WALLET] = size        # 0: 200, 1: 1000, 2: 5000

    def give(self, item):
        slot, bit, item_id, extra = ITEMS_GIVEN[item]
        self.q[GOT_ITEMS + slot] |= 1 << bit
        self.give_upgrade_bits(slot, bit)
        self.q[ITEMS + slot] = item_id
        for off, value in extra.items():
            if not self.q[off]:
                self.q[off] = value

    def give_upgrade_bits(self, slot, bit):
        # Upgraded versions (Deluxe Picto Box, Fire and Ice / Light Arrows) imply the earlier ones.
        for b in range(bit):
            self.q[GOT_ITEMS + slot] |= 1 << b

    def take(self, slot):
        self.q[ITEMS + slot] = 0xFF
        self.q[GOT_ITEMS + slot] = 0

    def equipment(self, index):
        current = self.q[EQUIP + index]
        for name, item_id, _ in EQUIPMENT[index][1]:
            if item_id == current:
                return name
        return 'none' if current == 0xFF else f'item 0x{current:02X}'

    def set_equipment(self, index, name):
        for n, item_id, bit in EQUIPMENT[index][1]:
            if n == name:
                self.q[EQUIP + index] = item_id
                self.q[COLLECT + index] = 0 if bit is None else (1 << (bit + 1)) - 1
                return
        raise ValueError(name)

    def bits(self, off):
        return [bool(self.q[off] & (1 << i)) for i in range(8)]

    def set_bits(self, off, flags):
        self.q[off] = sum(1 << i for i, on in enumerate(flags) if on)

    def set_restart(self, stage, room, point):
        self.q[RESTART:RESTART + 8] = stage.encode('ascii')[:7].ljust(8, b'\0')
        self.q[RESTART + 8] = room & 0xFF
        self.q[RESTART + 9] = point

    def set_flag(self, v, on=True):
        if on:
            self.q[FLAGS + (v >> 8)] |= v & 0xFF
        else:
            self.q[FLAGS + (v >> 8)] &= ~(v & 0xFF) & 0xFF

    def save(self, path):
        self.q[DATA:DATA + 8] = struct.pack('>Q', qsum(self.q))
        for copy in (0, 1):
            o = self._offset(copy)
            self.data[o:o + QUEST] = self.q
            block = HEADER + BLOCK * (1 + copy)
            self.data[block + BLOCK - 4:block + BLOCK] = struct.pack(
                '>I', block_checksum(self.data[block:block + BLOCK]))
        open(path, 'wb').write(self.data)


# ---- version 2: bottles, bags, capacities, Hero's Charm (all from d_item.cpp / d_save.cpp)
HEROS_CHARM = COLLECT + 4          # mCollect[4] bit 0 (item_func_heros_omamori)
BOTTLE_SLOTS = (14, 15, 16, 17)
# (name, item ID, (obtained byte, mask)) from dSv_player_get_item_c::onBottleItem
BOTTLE_CONTENTS = [
    ('none', 0xFF, None), ('Empty Bottle', 0x50, (0, 0x04)), ('Red Potion', 0x51, (0, 0x08)),
    ('Green Potion', 0x52, (0, 0x10)), ('Blue Potion', 0x53, (0, 0x20)),
    ('Elixir Soup (1/2)', 0x54, (0, 0x40)), ('Elixir Soup', 0x55, (0, 0x80)),
    ('Bottled Water', 0x56, (1, 0x02)), ('Fairy in Bottle', 0x57, (1, 0x04)),
    ('Forest Firefly', 0x58, (1, 0x08)), ('Forest Water', 0x59, (1, 0x10)),
]
BEAST, BAIT, RESERVE = 0x76, 0x7E, 0x86            # 8 bag slots each (item IDs)
RESERVE_FLAGS, BEAST_FLAGS, BAIT_FLAGS = 0x8E, 0x92, 0x93
BEAST_NUM, BAIT_NUM, RESERVE_NUM = 0x9A, 0xA2, 0xAA
SPOILS = [('Skull Necklace', 0x45), ('Boko Baba Seed', 0x46), ('Golden Feather', 0x47),
          ("Knight's Crest", 0x48), ('Red Chu Jelly', 0x49), ('Green Chu Jelly', 0x4A),
          ('Blue Chu Jelly', 0x4B), ('Joy Pendant', 0x1F)]          # index = dBeastIdx
BAITS = [('none', 0xFF), ('All-Purpose Bait', 0x82), ('Hyoi Pear', 0x83)]
DELIVERY = [(n, 0x8C + i) for i, n in enumerate([
    'Town Flower', 'Sea Flower', 'Exotic Flower', "Hero's Flag", 'Big Catch Flag', 'Big Sale Flag',
    'Pinwheel', 'Sickle Moon Flag', 'Skull Tower Idol', 'Fountain Idol', 'Postman Statue',
    'Shop Guru Statue', "Father's Letter", 'Note to Mom', "Maggie's Letter", "Moblin's Letter",
    'Cabana Deed', 'Complimentary ID', 'Fill-Up Coupon'])]
# 0x9F (Legendary Pictograph) is deliberately absent: its pickup function, item_func_salvage_item1,
# is empty in the decomp ("originally salvage item 1, but was repurposed"), so the game never puts
# it in the Delivery Bag; it lives with the Picto Box's pictographs instead.
CAPACITIES = [0, 30, 60, 99]       # bomb bag and quiver upgrades


def _bottle(self, i):
    current = self.q[ITEMS + BOTTLE_SLOTS[i]]
    for name, item_id, _ in BOTTLE_CONTENTS:
        if item_id == current:
            return name
    return f'item 0x{current:02X}'


def _set_bottle(self, i, name):
    for n, item_id, got in BOTTLE_CONTENTS:
        if n == name:
            self.q[ITEMS + BOTTLE_SLOTS[i]] = item_id
            if got:
                self.q[GOT_ITEMS + got[0]] |= got[1]
            return
    raise ValueError(name)


def _spoils(self):
    """{spoils name: count} for what is in the Spoils Bag."""
    out = {}
    for slot in range(8):
        for name, item_id in SPOILS:
            if self.q[BEAST + slot] == item_id:
                out[name] = self.q[BEAST_NUM + slot]
    return out


def _set_spoils(self, counts):
    """Counts by name; 0 removes. Types already in the bag keep their slot (setBeastItem)."""
    for slot in range(8):
        item_id = self.q[BEAST + slot]
        name = next((n for n, i in SPOILS if i == item_id), None)
        if name is not None and counts.get(name, 0) == 0:
            self.q[BEAST + slot], self.q[BEAST_NUM + slot] = 0xFF, 0
    for idx, (name, item_id) in enumerate(SPOILS):
        n = counts.get(name, 0)
        if not n:
            continue
        slots = [s for s in range(8) if self.q[BEAST + s] == item_id] or \
                [s for s in range(8) if self.q[BEAST + s] == 0xFF]
        self.q[BEAST + slots[0]] = item_id
        self.q[BEAST_NUM + slots[0]] = min(n, 99)
        self.q[BEAST_FLAGS] |= 1 << idx


def _bait(self):
    """[(name, count)] for the 8 Bait Bag slots."""
    names = {i: n for n, i in BAITS}
    return [(names.get(self.q[BAIT + s], f'item 0x{self.q[BAIT + s]:02X}'), self.q[BAIT_NUM + s])
            for s in range(8)]


def _set_bait(self, slots):
    for s, (name, count) in enumerate(slots):
        item_id = dict(BAITS)[name]
        self.q[BAIT + s] = item_id
        # Every way the game adds bait goes through setBaitItem, which fills a new slot with 3;
        # nothing ever raises a slot's count, and bait is used one at a time. A Hyoi Pear empties
        # its slot when used, so its count never matters (the game still writes 3).
        if item_id == 0xFF:
            self.q[BAIT_NUM + s] = 0
        elif item_id == 0x83:
            self.q[BAIT_NUM + s] = 3
        else:
            self.q[BAIT_NUM + s] = min(max(count, 1), 3)
        if item_id != 0xFF:
            self.q[BAIT_FLAGS] |= 1 << (item_id - 0x82)


def _delivery(self):
    ids = {self.q[RESERVE + s] for s in range(8)}
    return [n for n, i in DELIVERY if i in ids]


def _set_delivery(self, names):
    """Delivery Bag items by name (at most 8). Items kept stay in their slot."""
    wanted = [i for n, i in DELIVERY if n in names]
    if len(wanted) > 8:
        raise ValueError('the Delivery Bag holds 8 items')
    for s in range(8):
        if self.q[RESERVE + s] not in wanted:
            self.q[RESERVE + s], self.q[RESERVE_NUM + s] = 0xFF, 0
    flags = struct.unpack('>I', self.q[RESERVE_FLAGS:RESERVE_FLAGS + 4])[0]
    for item_id in wanted:
        if item_id not in self.q[RESERVE:RESERVE + 8]:
            s = list(self.q[RESERVE:RESERVE + 8]).index(0xFF)
            self.q[RESERVE + s], self.q[RESERVE_NUM + s] = item_id, 1
        flags |= 1 << (item_id - 0x8C)
    self.q[RESERVE_FLAGS:RESERVE_FLAGS + 4] = struct.pack('>I', flags)


def _set_bombs(self, capacity):
    if capacity:
        self.give('Bombs')
        self.q[BOMBS_MAX] = capacity
        self.q[BOMBS] = capacity
    else:
        self.take(13)
        self.q[BOMBS_MAX] = self.q[BOMBS] = 0


def _set_quiver(self, capacity):
    self.q[ARROWS_MAX] = capacity
    self.q[ARROWS] = capacity


Save.bottle, Save.set_bottle = _bottle, _set_bottle
Save.spoils, Save.set_spoils = _spoils, _set_spoils
Save.bait, Save.set_bait = _bait, _set_bait
Save.delivery, Save.set_delivery = _delivery, _set_delivery
Save.set_bombs, Save.set_quiver = _set_bombs, _set_quiver


# ---- disc reading: which stages, rooms and spawn points exist (read from the game's own files)
def disc_index(iso_path):
    """{'res/Stage/sea/Room44.arc': (disc offset, size), ...} from the disc's file system table.

    GameCube discs keep the FST offset and size at 0x424/0x428. Entries are 12 bytes: a flag
    and name offset, then for folders the parent and next index, for files the offset and size.
    """
    with open(iso_path, 'rb') as f:
        f.seek(0x424)
        fst_off, fst_size = struct.unpack('>II', f.read(8))
        f.seek(fst_off)
        fst = f.read(fst_size)
    count = struct.unpack('>I', fst[8:12])[0]
    names = fst[count * 12:]
    files, path, ends = {}, [], []
    for i in range(1, count):
        while ends and i >= ends[-1]:
            ends.pop()
            path.pop()
        word, a, b = struct.unpack('>III', fst[i * 12:i * 12 + 12])
        n = names[word & 0xFFFFFF:names.index(b'\0', word & 0xFFFFFF)].decode('ascii', 'replace')
        if word >> 24 == 1:
            path.append(n)
            ends.append(b)
        else:
            files['/'.join(path + [n])] = (a, b)
    return files


def disc_rooms(iso_path, index=None):
    """{stage name: set of room numbers} from res/Stage/<stage>/Room<N>.arc."""
    stages = {}
    for p in (index or disc_index(iso_path)):
        parts = p.split('/')
        if len(parts) == 4 and parts[:2] == ['res', 'Stage']:
            low = parts[3].lower()
            rooms = stages.setdefault(parts[2], set())
            if low.startswith('room') and low.endswith('.arc') and low[4:-4].isdigit():
                rooms.add(int(low[4:-4]))
    return stages


def yaz0_decompress(data):
    """Nintendo's Yaz0 compression: a group byte of 8 flags, each either a literal byte or a
    back-reference (2 bytes, plus a third for long lengths)."""
    if data[:4] != b'Yaz0':
        return data
    size = struct.unpack('>I', data[4:8])[0]
    out = bytearray()
    src = 16
    while len(out) < size:
        group = data[src]
        src += 1
        for bit in range(7, -1, -1):
            if len(out) >= size:
                break
            if group & (1 << bit):
                out.append(data[src])
                src += 1
            else:
                b1, b2 = data[src], data[src + 1]
                src += 2
                dist = ((b1 & 0x0F) << 8 | b2) + 1
                length = b1 >> 4
                if length == 0:
                    length = data[src] + 0x12
                    src += 1
                else:
                    length += 2
                for _ in range(length):
                    out.append(out[-dist])
    return bytes(out)


def rarc_files(data):
    """{file name: bytes} for the files in a RARC archive (Nintendo's archive format)."""
    data = yaz0_decompress(data)
    if data[:4] != b'RARC':
        raise ValueError('not a RARC archive')
    data_start = 0x20 + struct.unpack('>I', data[0x0C:0x10])[0]
    info = 0x20
    n_entries, entries_off = struct.unpack('>II', data[info + 8:info + 16])
    strings_off = struct.unpack('>I', data[info + 20:info + 24])[0]
    out = {}
    for i in range(n_entries):
        e = info + entries_off + i * 0x14
        _id, _hash, kind, name_off, off, size = struct.unpack('>HHHHII', data[e:e + 0x10])
        if kind & 0x0200:                       # folder (including "." and "..")
            continue
        s = info + strings_off + name_off
        name = data[s:data.index(b'\0', s)].decode('ascii', 'replace')
        out[name] = data[data_start + off:data_start + off + size]
    return out


def plyr_entries(dzx):
    """Player spawn points in a stage/room data file (.dzs/.dzr): the 'PLYR' chunk.

    Each 32-byte entry is an actor record; dStage_playerInit matches the requested spawn
    point against the low byte of the Z rotation, and takes the room from the entry's
    parameters (low 6 bits). Returns [(spawn id, room, x, y, z)].
    """
    chunks = struct.unpack('>I', dzx[0:4])[0]
    for c in range(chunks):
        tag, num, off = struct.unpack('>4sII', dzx[4 + c * 12:16 + c * 12])
        if tag == b'PLYR':
            out = []
            for i in range(num):
                e = dzx[off + i * 0x20:off + (i + 1) * 0x20]
                params = struct.unpack('>I', e[8:12])[0]
                x, y, z = struct.unpack('>fff', e[12:24])
                angle_z = struct.unpack('>H', e[0x1C:0x1E])[0]
                out.append((angle_z & 0xFF, params & 0x3F, x, y, z))
            return out
    return []


def spawn_points(iso_path, stage, room, index=None):
    """Spawn points the game can find for stage/room: {'room': [...], 'stage': [...]} as
    plyr_entries tuples. A restart whose point is in neither list makes the retail game read
    past the end of the list (the debug build's JUT_ASSERT(i != num)), which froze in testing."""
    index = index or disc_index(iso_path)

    def read(path):
        if path not in index:
            return None
        off, size = index[path]
        with open(iso_path, 'rb') as f:
            f.seek(off)
            return f.read(size)

    result = {'room': [], 'stage': []}
    for kind, arc, ext in (('room', f'res/Stage/{stage}/Room{room}.arc', '.dzr'),
                           ('stage', f'res/Stage/{stage}/Stage.arc', '.dzs')):
        data = read(arc)
        if data is None:
            continue
        for name, blob in rarc_files(data).items():
            if name.lower().endswith(ext):
                result[kind] = plyr_entries(yaz0_decompress(blob))
    return result


# ---- story presets: quest logs from real saves at known points in the story
NAME, OPTIONS = (0x157, 0x168), (0x19F, 0x1A4)     # player name; options (dSv_player_config_c)


def load_presets(folder):
    """[{'name', 'file', 'slot'}] from <folder>/presets.json (written by make_presets.py)."""
    import json
    import os
    try:
        presets = json.load(open(os.path.join(folder, 'presets.json'), encoding='utf-8'))
    except (OSError, ValueError):
        return []
    for p in presets:
        p['path'] = os.path.join(folder, p['file'])
    return [p for p in presets if os.path.isfile(p['path'])]


def preset_quest(preset, current):
    """The preset's quest log, keeping the current save's player name and options."""
    q = bytearray(Save(preset['path'], preset.get('slot', 1)).q)
    for a, b in (NAME, OPTIONS):
        q[a:b] = current.q[a:b]
    return bytes(q)


# Items the main story requires (given by the story or needed to progress). Everything else
# (Tingle Tuner, Picto Box, Magic Armor, Bait Bag, bottles, wallet/quiver/bomb upgrades,
# Hero's Charm, heart pieces...) is optional and left as the player has it.
MANDATORY_ITEMS = ['Telescope', "Boat's Sail", 'Wind Waker', 'Spoils Bag', 'Grappling Hook', 'Delivery Bag',
                   'Deku Leaf', 'Boomerang', 'Bombs', 'Iron Boots', 'Skull Hammer', 'Hookshot']
BOW_ORDER = ["Hero's Bow", 'Fire and Ice Arrows', 'Light Arrows']
OPTIONAL_SONGS = (1 << 1) | (1 << 5)           # Ballad of Gales, Song of Passing (kept if still earnable)
# Story flags recording how each song was learned (ZeldaSpeedRuns sheet). They follow the song:
# a song in the collection has its flags on, a song taken away has them off.
SONG_FLAGS = {
    0: [0x2708],                           # Wind's Requiem: Learn Wind's Requiem
    1: [0x2710, 0x3E40, 0x3E20],           # Ballad of Gales: Defeat Cyclos, warped by Cyclos, KoRL's text
    2: [0x2510],                           # Command Melody: Learn Command Melody
    5: [0x0C40],                           # Song of Passing: Learn Song of Passing
}
MEMORY = 0x374                     # 16 per-area progress blocks of 0x24 (dSv_memory_c)
BOSS_BITS = (1 << 3) | (1 << 5)    # mDungeonItem: STAGE_BOSS_ENEMY (beaten), STAGE_BOSS_DEMO (scene seen)
DUNGEON_AREAS = {2: 'Forsaken Fortress', 3: 'Dragon Roost Cavern', 4: 'Forbidden Woods', 5: 'Tower of the Gods',
                 6: 'Earth Temple', 7: 'Wind Temple', 8: "Ganon's Tower"}   # dSv_save_c STAGE_* numbers


def preset_story_only(preset, current, mandatory_flag):
    """Set the story's required progress to match a preset, forwards or backwards.

    Required items, the bow level, sword/shield/bracelets, required songs, pearls, Triforce
    shards, story flags that mandatory_flag(v) accepts, and each dungeon's 'boss beaten' are
    made to match the preset (given or taken away). A dungeon the player has beaten but the
    preset has not is reset to the preset's state of it. Takes the preset's restart place.
    Optional progress (hearts, rupees, bags, bottles, charts, side quests, optional items and
    songs) stays as it is. Returns (quest bytes, list of what changed).
    """
    p = Save(preset['path'], preset.get('slot', 1))
    s = Save.__new__(Save)
    s.data, s.slot, s.q = current.data, current.slot, bytearray(current.q)
    done = []
    for item in MANDATORY_ITEMS:
        want, have = p.has(item), s.has(item)
        if want and not have:
            s.give(item)
            done.append(f'gave {item}')
        elif have and not want:
            s.take(ITEMS_GIVEN[item][0])
            done.append(f'removed {item}')

    def bow(x):
        return next((b for b in reversed(BOW_ORDER) if x.q[ITEMS + 12] == ITEMS_GIVEN[b][2]), None)
    want, have = bow(p), bow(s)
    if want != have:
        if want:
            s.take(12)
            s.give(want)
            if not s.q[ARROWS_MAX]:
                s.set_quiver(30)
        else:
            s.take(12)
        done.append(f'bow: {want or "none"}')
    for i, (part, options) in enumerate(EQUIPMENT):
        want, have = p.equipment(i), s.equipment(i)
        if want != have and want in [o[0] for o in options]:
            s.set_equipment(i, want)
            done.append(f'{part.lower()}: {want}')
    songs = (s.q[SONGS] & OPTIONAL_SONGS) | (p.q[SONGS] & ~OPTIONAL_SONGS & 0xFF)
    # Optional songs still need what earns them: the Ballad of Gales comes from shooting Cyclos
    # (needs a bow), the Song of Passing from Tott, who wants the Wind Waker played.
    if not bow(p):
        songs &= ~(1 << 1) & 0xFF
    if not p.has('Wind Waker'):
        songs &= ~(1 << 5) & 0xFF
    if songs != s.q[SONGS]:
        s.q[SONGS] = songs
        done.append('songs: ' + (', '.join(n for i, n in enumerate(SONG_NAMES) if songs & (1 << i)) or 'none'))
    for off, label in ((PEARLS, 'pearls'), (SHARDS, 'Triforce shards')):
        if s.q[off] != p.q[off]:
            s.q[off] = p.q[off]
            done.append(f'{label}: {bin(p.q[off]).count("1")}')
    if not p.q[MAGIC_MAX] and s.q[MAGIC_MAX]:
        s.q[MAGIC_MAX] = s.q[MAGIC] = 0
        done.append('no magic meter')
    elif p.q[MAGIC_MAX] and not s.q[MAGIC_MAX]:
        s.q[MAGIC_MAX] = s.q[MAGIC] = 16
        done.append('magic meter')
    song_flags = {v for vs in SONG_FLAGS.values() for v in vs}
    for bit, flags in SONG_FLAGS.items():
        for v in flags:
            s.set_flag(v, bool(s.q[SONGS] & (1 << bit)) and (p.flag(v) or s.flag(v)))
    on = off = 0
    for byte in range(0x100):
        for bit in range(8):
            v = byte << 8 | (1 << bit)
            if v in song_flags:
                continue
            if p.flag(v) != s.flag(v) and mandatory_flag(v):
                s.set_flag(v, p.flag(v))
                on, off = on + p.flag(v), off + (not p.flag(v))
    if on or off:
        done.append(f'story flags: {on} turned on, {off} turned off')
    for stage in range(16):
        start = MEMORY + stage * 0x24
        want, have = p.q[start + 0x21] & BOSS_BITS, s.q[start + 0x21] & BOSS_BITS
        if want == have:
            continue
        if have and not want and stage in DUNGEON_AREAS:
            s.q[start:start + 0x24] = p.q[start:start + 0x24]
            done.append(f'{DUNGEON_AREAS[stage]} reset to how the preset had it')
        else:
            s.q[start + 0x21] = (s.q[start + 0x21] & ~BOSS_BITS & 0xFF) | want
            done.append(f'{DUNGEON_AREAS.get(stage, f"area {stage}")}: boss {"beaten" if want else "not beaten"}')
    if s.q[RESTART:RESTART + 0x0C] != p.q[RESTART:RESTART + 0x0C]:
        s.q[RESTART:RESTART + 0x0C] = p.q[RESTART:RESTART + 0x0C]
        done.append('restart place {} {} {}'.format(*p.restart()))
    return bytes(s.q), done


# ---- sea chart: which of the 49 squares are drawn (mFmapBits bit 0)
FMAP = 0xBF + 0x40                 # mFmapBits in the card quest log, one byte per sea square
CHART_DEFAULTS = (0, 10, 43)       # drawn on a new file: Forsaken Fortress, Windfall, Outset


def _chart_drawn(self):
    return sum(self.q[FMAP + i] & 1 for i in range(49))


def _set_chart(self, mode):
    """'reveal': draw every square, as Better Wind Waker's option does on a new file
    (wwrando reveal_sea_chart.asm). 'reset': only the new-file defaults (dSv_player_map_c::init);
    squares fishmen drew are cleared too. 'Link has sailed here' (bit 1) is left alone."""
    for i in range(49):
        if mode == 'reveal' or i in CHART_DEFAULTS:
            self.q[FMAP + i] |= 1
        else:
            self.q[FMAP + i] &= 0xFE


Save.chart_drawn, Save.set_chart = _chart_drawn, _set_chart


def sync_song_flags(save, before):
    """After songs are edited by hand: turn each changed song's 'learned' flags on or off with it."""
    changed = save.q[SONGS] ^ before
    for bit, flags in SONG_FLAGS.items():
        if changed & (1 << bit):
            for v in flags:
                save.set_flag(v, bool(save.q[SONGS] & (1 << bit)))
