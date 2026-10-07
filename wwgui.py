r"""Wind Waker save editor: a window over wwedit.py.

Run:  python wwgui.py
Pick a catalog entry and quest log, change things on the tabs, then save as a new catalog
entry (and optionally put it into a test build's card, slot 3). The source entry is never
modified. Needs wwedit.py and wwcat.py in the same folder (wwcat supplies the flag names).
"""
import glob
import os
import shutil
import subprocess
import sys
import json
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wwedit  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
import wwcat   # noqa: E402

import config  # noqa: E402

INJECT = config.path('inject')
SETTINGS = os.path.join(config.ROOT, 'wwgui-settings.json')
PRESETS = config.path('presets')
PRESET_FOLDERS = [PRESETS]
WALLETS = ['200', '1000', '5000']
MAGIC = [('None', 0), ('Normal', 16), ('Double', 32)]
TOGGLES = ['Telescope', "Boat's Sail", 'Wind Waker', 'Grappling Hook', 'Spoils Bag', 'Boomerang',
           'Deku Leaf', 'Tingle Tuner', 'Iron Boots', 'Magic Armor', 'Bait Bag', 'Delivery Bag',
           'Hookshot', 'Skull Hammer']
PICTO = ['none', 'Picto Box', 'Deluxe Picto Box']
BOWS = ['none', "Hero's Bow", 'Fire and Ice Arrows', 'Light Arrows']

# Spawn spots: (name, stage, room, point). The first ones are from this playthrough's saves;
# the rest are entrance spawns from the Wind Waker Randomizer's randomizers/entrances.py.
SEEN_SPOTS = [
    ('Outset Island: new game start', 'sea', 44, 206),
    ('Outset Island: story restart point', 'sea', 44, 128),
    ('Windfall Island: post-rescue alcove', 'sea', 11, 128),
]
RESTART_SPOTS = [
    ('Dungeon Entrance on Dragon Roost Island', 'Adanmae', 0, 2),
    ('Dungeon Entrance in Forest Haven Sector', 'sea', 41, 6),
    ('Dungeon Entrance in Tower of the Gods Sector', 'sea', 26, 2),
    ('Dungeon Entrance on Headstone Island', 'Edaichi', 0, 1),
    ('Dungeon Entrance on Gale Isle', 'Ekaze', 0, 1),
    ('Dragon Roost Cavern', 'M_NewD2', 0, 0),
    ('Forbidden Woods', 'kindan', 0, 0),
    ('Tower of the Gods', 'Siren', 0, 0),
    ('Earth Temple', 'M_Dai', 0, 0),
    ('Wind Temple', 'kaze', 15, 15),
    ('Miniboss Entrance in Forbidden Woods', 'kindan', 9, 1),
    ('Miniboss Entrance in Tower of the Gods', 'Siren', 14, 1),
    ('Miniboss Entrance in Earth Temple', 'M_Dai', 7, 9),
    ('Miniboss Entrance in Wind Temple', 'kaze', 2, 20),
    ('Miniboss Entrance in Hyrule Castle', 'Hyroom', 0, 2),
    ('Forbidden Woods Miniboss Arena', 'kinMB', 10, 0),
    ('Tower of the Gods Miniboss Arena', 'SirenMB', 23, 0),
    ('Earth Temple Miniboss Arena', 'M_DaiMB', 12, 0),
    ('Wind Temple Miniboss Arena', 'kazeMB', 6, 0),
    ('Master Sword Chamber', 'kenroom', 0, 0),
    ('Boss Entrance in Dragon Roost Cavern', 'M_NewD2', 10, 27),
    ('Boss Entrance in Forbidden Woods', 'kindan', 16, 1),
    ('Boss Entrance in Tower of the Gods', 'Siren', 18, 27),
    ('Boss Entrance in Forsaken Fortress', 'sea', 1, 27),
    ('Boss Entrance in Earth Temple', 'M_Dai', 15, 27),
    ('Boss Entrance in Wind Temple', 'kaze', 12, 27),
    ('Gohma Boss Arena', 'M_DragB', 0, 0),
    ('Kalle Demos Boss Arena', 'kinBOSS', 0, 0),
    ('Gohdan Boss Arena', 'SirenB', 0, 0),
    ('Helmaroc King Boss Arena', 'M2tower', 0, 16),
    ('Jalhalla Boss Arena', 'M_DaiB', 0, 0),
    ('Molgera Boss Arena', 'kazeB', 0, 0),
    ('Secret Cave Entrance on Outset Island', 'sea', 44, 10),
    ('Secret Cave Entrance on Dragon Roost Island', 'sea', 13, 5),
    ('Secret Cave Entrance on Fire Mountain', 'sea', 20, 0),
    ('Secret Cave Entrance on Ice Ring Isle', 'sea', 40, 0),
    ('Secret Cave Entrance on Private Oasis', 'Abesso', 0, 1),
    ('Secret Cave Entrance on Needle Rock Isle', 'sea', 29, 5),
    ('Secret Cave Entrance on Angular Isles', 'sea', 47, 5),
    ('Secret Cave Entrance on Boating Course', 'sea', 48, 5),
    ('Secret Cave Entrance on Stone Watcher Island', 'sea', 31, 1),
    ('Secret Cave Entrance on Overlook Island', 'sea', 7, 1),
    ("Secret Cave Entrance on Bird's Peak Rock", 'sea', 35, 1),
    ('Secret Cave Entrance on Pawprint Isle', 'sea', 12, 1),
    ('Secret Cave Entrance on Pawprint Isle Side Isle', 'sea', 12, 5),
    ('Secret Cave Entrance on Diamond Steppe Island', 'sea', 36, 1),
    ('Secret Cave Entrance on Bomb Island', 'sea', 34, 1),
    ('Secret Cave Entrance on Rock Spire Isle', 'sea', 16, 1),
    ('Secret Cave Entrance on Shark Island', 'sea', 38, 5),
    ('Secret Cave Entrance on Cliff Plateau Isles', 'sea', 42, 2),
    ('Secret Cave Entrance on Horseshoe Island', 'sea', 43, 5),
    ('Secret Cave Entrance on Star Island', 'sea', 2, 1),
    ('Savage Labyrinth', 'Cave09', 0, 0),
    ('Dragon Roost Island Secret Cave', 'TF_06', 0, 0),
    ('Fire Mountain Secret Cave', 'MiniKaz', 0, 0),
    ('Ice Ring Isle Secret Cave', 'MiniHyo', 0, 0),
    ('Cabana Labyrinth', 'TF_04', 0, 0),
    ('Needle Rock Isle Secret Cave', 'SubD42', 0, 0),
    ('Angular Isles Secret Cave', 'SubD43', 0, 0),
    ('Boating Course Secret Cave', 'SubD71', 0, 0),
    ('Stone Watcher Island Secret Cave', 'TF_01', 0, 0),
    ('Overlook Island Secret Cave', 'TF_02', 0, 0),
    ("Bird's Peak Rock Secret Cave", 'TF_03', 0, 0),
    ('Pawprint Isle Chuchu Cave', 'TyuTyu', 0, 0),
    ('Pawprint Isle Wizzrobe Cave', 'Cave07', 0, 0),
    ('Diamond Steppe Island Warp Maze Cave', 'WarpD', 0, 0),
    ('Bomb Island Secret Cave', 'Cave01', 0, 0),
    ('Rock Spire Isle Secret Cave', 'Cave04', 0, 0),
    ('Shark Island Secret Cave', 'ITest63', 0, 0),
    ('Cliff Plateau Isles Secret Cave', 'Cave03', 0, 0),
    ('Horseshoe Island Secret Cave', 'Cave05', 0, 0),
    ('Star Island Secret Cave', 'Cave02', 0, 0),
    ('Inner Entrance in Ice Ring Isle Secret Cave', 'MiniHyo', 0, 0),
    ('Inner Entrance in Cliff Plateau Isles Secret Cave', 'Cave03', 0, 1),
    ('Ice Ring Isle Inner Cave', 'ITest62', 0, 0),
    ('Cliff Plateau Isles Inner Cave', 'sea', 42, 1),
    ('Fairy Fountain Entrance on Outset Island', 'A_mori', 0, 2),
    ('Fairy Fountain Entrance on Thorned Fairy Island', 'sea', 28, 1),
    ('Fairy Fountain Entrance on Eastern Fairy Island', 'sea', 19, 1),
    ('Fairy Fountain Entrance on Western Fairy Island', 'sea', 15, 1),
    ('Fairy Fountain Entrance on Southern Fairy Island', 'sea', 39, 1),
    ('Fairy Fountain Entrance on Northern Fairy Island', 'sea', 3, 1),
    ('Outset Fairy Fountain', 'Fairy04', 0, 0),
    ('Thorned Fairy Fountain', 'Fairy05', 0, 0),
    ('Eastern Fairy Fountain', 'Fairy02', 0, 0),
    ('Western Fairy Fountain', 'Fairy03', 0, 0),
    ('Southern Fairy Fountain', 'Fairy06', 0, 0),
    ('Northern Fairy Fountain', 'Fairy01', 0, 0),
]

ALL_SPOTS = SEEN_SPOTS + RESTART_SPOTS
# Stage descriptions from the Wind Waker Randomizer (data/stage_names.txt, MIT licence).
STAGE_NAMES = {
    'Abesso': 'Cabana Interior',
    'Abship': 'Submarines',
    'Adanmae': 'Dragon Roost Cavern Entrance',
    'ADMumi': 'Tower of the Gods Raising and Bell Ringing Cutscenes',
    'Amos_T': 'Unused',
    'Asoko': 'Pirate Ship Interior',
    'Atorizk': 'Rito Aerie',
    'A_mori': 'Outset Island Fairy Woods',
    'A_nami': 'Unused',
    'A_R00': 'Unused',
    'A_umikz': 'Sea During Pirate Ship Ride To Forsaken Fortress',
    'Cave01': 'Bomb Island Cave',
    'Cave02': 'Star Island Cave',
    'Cave03': 'Cliff Plateau Isles Cave',
    'Cave04': 'Rock Spire Isle Cave',
    'Cave05': 'Horseshoe Island Cave',
    'Cave06': 'Unused',
    'Cave07': 'Pawprint Isle Wizzrobe Cave',
    'Cave08': 'Unused',
    'Cave09': 'Savage Labyrinth',
    'Cave10': 'Savage Labyrinth',
    'Cave11': 'Savage Labyrinth',
    'Comori': "Komali's Room",
    'DmSpot0': 'Unused',
    'E3ROOP': 'Unused',
    'Ebesso': 'Unused',
    'Edaichi': 'Earth Temple Entrance',
    'Ekaze': 'Wind Temple Entrance',
    'ENDumi': 'Ending',
    'Fairy01': 'Northern Fairy Island Fairy Fountain',
    'Fairy02': 'Eastern Fairy Island Fairy Fountain',
    'Fairy03': 'Western Fairy Island Fairy Fountain',
    'Fairy04': 'Outset Island Fairy Fountain',
    'Fairy05': 'Thorned Fairy Island Fairy Fountain',
    'Fairy06': 'Southern Fairy Island Fairy Fountain',
    'figureA': 'Nintendo Gallery Hall A',
    'figureB': 'Nintendo Gallery Hall B',
    'figureC': 'Nintendo Gallery Hall C',
    'figureD': 'Nintendo Gallery Hall D',
    'figureE': 'Nintendo Gallery Hall E',
    'figureF': 'Nintendo Gallery Hall F',
    'figureG': 'Nintendo Gallery Hall G',
    'GanonA': "Ganon's Tower Entrance",
    'GanonB': "Ganon's Tower Before Gohma Rematch",
    'GanonC': "Ganon's Tower Before Molgera Rematch",
    'GanonD': "Ganon's Tower Before Kalle Demos Rematch",
    'GanonE': "Ganon's Tower Before Jalhalla Rematch",
    'GanonJ': "Ganon's Tower Maze",
    'GanonK': "Ganon's Tower Puppet Ganon",
    'GanonL': "Ganon's Tower Stairs To Puppet Ganon",
    'GanonM': "Ganon's Tower Phantom Ganon",
    'GanonN': "Ganon's Tower Stairs To Phantom Ganon",
    'GTower': "Ganon's Tower - Rooftop",
    'Hyroom': 'Hyrule Castle Interior',
    'Hyrule': 'Hyrule Castle',
    'H_test': 'Unused',
    'ITest61': 'Unused',
    'ITest62': 'Ice Ring Isle Inner Cave',
    'ITest63': 'Shark Island Cave',
    'I_SubAN': 'Unused',
    'I_TestM': 'Unused',
    'I_TestR': 'Unused',
    'Kaisen': 'Squid Hunt Minigame',
    'KATA_HB': 'Unused',
    'KATA_RM': 'Unused',
    'kazan': 'Unused',
    'kaze': 'Wind Temple',
    'kazeB': 'Wind Temple Molgera Boss Room',
    'kazeMB': 'Wind Temple Wizzrobe Miniboss Room',
    'kenroom': 'Master Sword Chamber',
    'kinBOSS': 'Forbidden Woods Kalle Demos Boss Room',
    'kindan': 'Forbidden Woods',
    'kinMB': 'Forbidden Woods Mothula Miniboss Room',
    'K_Test2': 'Unused',
    'K_Test3': 'Unused',
    'K_Test4': 'Unused',
    'K_Test5': 'Unused',
    'K_Test6': 'Unused',
    'K_Test8': 'Unused',
    'K_Test9': 'Unused',
    'K_Testa': 'Unused',
    'K_Testb': 'Unused',
    'K_Testc': 'Unused',
    'K_Testd': 'Unused',
    'K_Teste': 'Unused',
    'LinkRM': "Link's House",
    'LinkUG': "Underneath Link's House",
    'M2ganon': "Forsaken Fortress Ganon's Room (2nd visit)",
    'M2tower': 'Forsaken Fortress Tower (2nd visit)',
    'ma2room': 'Forsaken Fortress Interior (2nd visit)',
    'ma3room': 'Forsaken Fortress Interior (3rd visit)',
    'majroom': 'Forsaken Fortress Interior (1st visit)',
    'MajyuE': 'Forsaken Fortress Exterior (1st visit)',
    'MiniHyo': 'Ice Ring Isle Cave',
    'MiniKaz': 'Fire Mountain Cave',
    'Mjtower': 'Forsaken Fortress Tower (1st visit)',
    'morocam': 'Unused',
    'Msmoke': 'Unused',
    'Mukao': 'Unused',
    'M_Dai': 'Earth Temple',
    'M_DaiB': 'Earth Temple Jalhalla Boss Room',
    'M_DaiMB': 'Earth Temple Stalfos Miniboss Room',
    'M_Dra09': 'Dragon Roost Cavern Moblin Miniboss Room',
    'M_DragB': 'Dragon Roost Cavern Gohma Boss Room',
    'M_NewD2': 'Dragon Roost Cavern',
    'Name': 'File Select Screen',
    'Nitiyou': "Mrs. Marie's School",
    'Obombh': 'Windfall Island Bomb Shop',
    'Obshop': "Beedle's Shop Ship",
    'Ocean': 'Boating Course Minigame',
    'Ocmera': "Lenzo's House",
    'Ocrogh': "Hollo's Forest Potion Shop",
    'Ojhous': "Orca's Room",
    'Ojhous2': "Sturgeon's Room",
    'Omasao': "Mesa the Grasscutter's House",
    'Omori': 'Forest Haven Interior',
    'Onobuta': "Rose's House",
    'Opub': 'Windfall Island Cafe Bar',
    'Orichh': 'House of Wealth',
    'Otkura': 'Cave Behind Forest Haven Waterfall',
    'Pdrgsh': 'Chu Jelly Juice Shop',
    'Pfigure': 'Nintendo Gallery Main Room',
    'Pjavdou': "Jabun's Cave",
    'Pnezumi': 'Windfall Town Jail',
    'PShip': 'Ghost Ship',
    'PShip2': 'Unused',
    'PShip3': 'Unused',
    'sea': 'The Great Sea',
    'sea_E': 'Unused',
    'sea_T': 'Title Screen',
    'ShipD': 'Islet of Steel Interior',
    'Siren': 'Tower of the Gods',
    'SirenB': 'Tower of the Gods Gohdan Boss Room',
    'SirenMB': 'Tower of the Gods Darknut Miniboss Room',
    'SubD42': 'Needle Rock Isle Cave',
    'SubD43': 'Angular Isles Cave',
    'SubD44': 'Unused',
    'SubD45': 'Unused',
    'SubD51': 'Unused',
    'SubD71': 'Boating Course Cave',
    'TEST': 'Unused',
    'TF_01': 'Stone Watcher Island Cave',
    'TF_02': 'Overlook Island Cave',
    'TF_03': "Bird's Peak Rock Cave",
    'TF_04': 'Cabana Labyrinth',
    'TF_05': 'Unused',
    'TF_06': 'Dragon Roost Island Secret Cave',
    'TF_07': 'Unused',
    'tincle': 'Unused',
    'TyuTyu': 'Pawprint Isle Chuchu Cave',
    'VrTest': 'Unused',
    'WarpD': 'Diamond Steppe Island Warp Maze',
    'Xboss0': 'Gohma Rematch',
    'Xboss1': 'Kalle Demos Rematch',
    'Xboss2': 'Jalhalla Rematch',
    'Xboss3': 'Molgera Rematch',
}

# Story flags are grouped into areas by keywords in their descriptions (rough, first match wins).
FLAG_AREAS = [
    ('Unused', ['unused']),
    ('King of Red Lions', ['korl', 'king of red lions', 'south wind']),
    ('Hyrule', ['tetra to zelda transformation']),          # before Prologue's 'tetra'
    ("Ganon's Tower", ["ganon's tower", 'puppet ganon', 'trial door', 'memory ', 'recollection',
                       'dark portal', 'ganondorf', 'phantom ganon wall', 'triforce']),
    ('Earth Temple', ['earth temple', ' et ', 'in et', 'jalhalla', 'headstone', "earth god", 'egl']),
    ('Wind Temple', ['wind temple', ' wt ', 'in wt', 'molgera', 'gale isle', 'gale island', "wind god", 'wga']),
    ('Tower of the Gods', ['totg', 'tower of the gods', 'gohdan', 'command melody', 'tower cutscene']),
    ('Forsaken Fortress', ['ff1', 'ff2', 'ff3', 'forsaken', 'helmaroc', 'phantom ganon', 'searchlight',
                           'barrel launch', 'jail', 'ems cutscene']),
    ('Prologue and Outset', ['prologue', 'outset', 'orca', 'grandma', 'aryll', 'sturgeon', 'forest of fairies',
                             "hero's clothes", "hero's sword", 'pirate ship', 'tetra', 'niko', 'rope game',
                             'spoils bag', 'gossip stone', 'rose', ' abe ', 'fat pig']),
    ('Dragon Roost', ['dri', 'drc', 'dragon roost', 'komali', 'medli', 'rito', 'valoo', 'gohma', 'quill',
                      "din's pearl", 'mapfish', 'map fish', 'grappling a bar']),
    ('Forest Haven and Forbidden Woods', ['forest haven', ' fh', 'deku', 'korok', 'makar', 'forbidden woods',
                                         'kalle demos', 'olivio', 'elma', 'linder', 'drona', 'irch', 'rown',
                                         'oakin', 'aldo', "farore's pearl", 'hollo']),
    ('Minigames and side quests', ['minigame', 'heart piece', 'nintendo gallery', 'carlov', 'manny', 'figurine',
                                   'boating course', 'spectacle', 'withered tree', 'sploosh']),
    ('Windfall', ['windfall', 'zunari', 'auction', 'lenzo', 'mila', 'maggie', 'maggy', 'tott', 'killer bee',
                  'marie', 'hide and seek', 'kreeb', 'gillian', 'cafe', 'potion', 'gossack', 'baito',
                  'bomb shop', 'password', 'endless night', 'sam ', 'loot', 'koboli', 'ivan', 'jan ', 'jin ',
                  'jun-roberto', 'mail', 'postman', 'lighthouse', 'decorat', 'hoskit', 'missy', 'minenco',
                  'garrickson', 'linda', 'anton', 'kamo', 'gummy', 'doc bandam', 'gossip ladies', 'windmill',
                  'potova', 'johanna', 'dampa']),
    ('Great Sea and islands', ['fairy', 'island', 'isle', 'tingle', 'beedle', 'salvage', 'ghost ship', 'fishman',
                               'chart', 'goron', 'cyclos', 'octo', 'nayru', 'jabun', 'submarine', 'platform',
                               'whirlpool', 'cabana', 'needle rock', 'golden ship', 'fcp', 'm&c']),
    ('Hyrule', ['hyrule 1', 'hyrule 3', 'in hyrule', 'hyrule puzzle', 'hyrule barrier', 'leave hyrule',
                'ms chamber', 'master sword cutscene', 'courtyard', 'darknut', 'tetra to zelda']),
    ('Items and songs', ['learn ', 'obtain ', 'chest', 'delivery bag']),
]
# Shown (and sorted) roughly in story order; matching above uses its own priority order.
FLAG_AREA_NAMES = ['All areas', 'Prologue and Outset', 'Forsaken Fortress', 'King of Red Lions', 'Windfall',
                   'Dragon Roost', 'Forest Haven and Forbidden Woods', 'Great Sea and islands',
                   'Tower of the Gods', 'Hyrule', 'Earth Temple', 'Wind Temple', "Ganon's Tower",
                   'Minigames and side quests', 'Items and songs', 'Unused', 'Other']
assert set(FLAG_AREA_NAMES[1:-1]) == {a for a, _ in FLAG_AREAS}


def flag_area(about):
    if not about:
        return 'Other'
    text = f' {about.lower()} '
    for area, words in FLAG_AREAS:
        if any(w in text for w in words):
            return area
    return 'Other'


# Story flags a "story progress only" preset leaves alone: side content, not the main story.
OPTIONAL_FLAG_WORDS = ['talk to', 'heart piece', 'minigame', 'auction', 'gallery', 'figurine', 'hide and seek',
                       'treasure chart', 'salvage', 'upgrade', 'wallet', 'quiver', 'bomb bag', 'rupee', 'tingle',
                       'withered tree', 'joy pendant', 'skull necklace', "knight's crest", 'golden feather',
                       'mail', 'potion', 'picto', 'decorat', 'lighthouse', 'pig', 'sploosh', 'beedle',
                       'unused', 'should exist', 'trade', 'first time', 'gossip ladies', 'killer bee',
                       'double magic']


def mandatory_flag(v):
    about = wwcat.describe_flag(v, *next(((n, c) for f, n, c in wwcat.FLAG_BITS if f == v), ('', '')))
    if not about:
        return False
    text = about.lower()
    if flag_area(about) in ('Minigames and side quests', 'Unused'):
        return False
    if 'korl' in text:               # the King's texts gate entering him: keep them
        return True
    return not any(w in text for w in OPTIONAL_FLAG_WORDS)


def stage_experimental(stage):
    """Unused, unknown and cutscene-only stages: hidden unless the experimental box is ticked."""
    about = STAGE_NAMES.get(stage, '')
    return not about or about.lower().startswith('unused') or 'cutscene' in about.lower()


def stage_label(stage):
    return f'{stage} \u2014 {STAGE_NAMES[stage]}' if stage in STAGE_NAMES else stage
SLOT_ITEMS = {}
for _name, (_slot, _bit, _id, _extra) in wwedit.ITEMS_GIVEN.items():
    SLOT_ITEMS.setdefault(_slot, []).append(_name)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Wind Waker save editor')
        self.minsize(1050, 900)
        self.source_path = self.source_label = None
        self.save = None
        self.initial = {}
        self.flag_changes = {}
        self.build()

    # ---------------------------------------------------------------- layout
    def build(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill='x')
        ttk.Button(top, text='Open card\u2026', command=self.open_card).grid(row=0, column=0)
        ttk.Button(top, text='Open .gci\u2026', command=self.open_gci).grid(row=0, column=1, padx=6)
        ttk.Label(top, text='Quest log').grid(row=0, column=2, padx=(12, 4))
        self.slot_box = ttk.Combobox(top, width=3, state='readonly', values=['1', '2', '3'])
        self.slot_box.set('1')
        self.slot_box.grid(row=0, column=3)
        self.slot_box.bind('<<ComboboxSelected>>', lambda e: self.source_path and self.load())
        ttk.Button(top, text='Revert', command=lambda: self.source_path and self.load()).grid(row=0, column=4, padx=(12, 0))
        self.info = ttk.Label(top, text='Open a memory card or a .gci save to start.')
        self.info.grid(row=0, column=5, sticky='w', padx=12)
        top.columnconfigure(5, weight=1)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=8)
        link = ttk.Frame(nb, padding=8)
        nb.add(link, text='Link')
        inventory = ttk.Frame(nb, padding=8)
        nb.add(inventory, text='Inventory')
        self.tab_help(link)
        self.tab_presets(self.section(link, 0))
        self.tab_status(self.section(link, 1))
        self.tab_equipment(self.section(link, 2))
        self.tab_quest(self.section(link, 3))
        self.tab_items(self.section(inventory, 0))
        self.tab_bags(self.section(inventory, 1))
        self.tab_restart(nb)
        self.tab_flags(nb)

        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill='x')
        ttk.Label(bottom, text='Write to card').grid(row=0, column=0, sticky='w')
        self.card_path = ttk.Entry(bottom, width=60)
        self.card_path.grid(row=0, column=1, sticky='we', padx=6)
        ttk.Button(bottom, text='Browse\u2026', command=self.pick_card).grid(row=0, column=2)
        slot = ttk.Frame(bottom)
        slot.grid(row=0, column=3, padx=6)
        ttk.Label(slot, text='as quest log').pack(side='left')
        self.target_slot = ttk.Combobox(slot, width=3, state='readonly', values=['1', '2', '3'])
        self.target_slot.set('3')
        self.target_slot.pack(side='left', padx=4)
        ttk.Button(bottom, text='Write to card', command=lambda: self.finish('card')).grid(row=0, column=4, padx=2)
        extra = ttk.Frame(bottom)
        extra.grid(row=1, column=0, columnspan=5, sticky='we', pady=(6, 0))
        ttk.Button(extra, text='Review changes', command=self.review).pack(side='left')
        ttk.Button(extra, text='Save a copy as .gci\u2026', command=lambda: self.finish('copy')).pack(side='left', padx=6)
        settings = self.settings()
        bottom.columnconfigure(1, weight=1)
        cards = config.cards()
        self.card_path.insert(0, settings.get('card') or (cards[0] if cards else ''))
        self.status = ttk.Label(self, relief='sunken', anchor='w', padding=4, text='Ready.')
        self.status.pack(fill='x', side='bottom')

    @staticmethod
    def section(parent, row):
        f = ttk.Frame(parent)
        f.grid(row=row, column=0, sticky='nw', pady=(0, 6))
        return f

    @staticmethod
    def radios(parent, title, var, options, row, column, **grid):
        box = ttk.LabelFrame(parent, text=title, padding=6)
        box.grid(row=row, column=column, sticky='nw', padx=6, pady=4, **grid)
        for i, (text, value) in enumerate(options):
            ttk.Radiobutton(box, text=text, variable=var, value=value).grid(row=i, column=0, sticky='w')
        return box

    def tab_help(self, parent):
        box = ttk.LabelFrame(parent, text='How to use', padding=10)
        box.grid(row=0, column=1, rowspan=4, sticky='nw', padx=(12, 0))
        steps = [
            ('1.  Close BlueWake.', 'The game keeps its memory card open while running and could overwrite your '
             'changes when it saves.'),
            ('2.  Open card\u2026', 'Pick your card (%APPDATA%\\BlueWake\\GZLE01.card, or user\\GZLE01.card in '
             'a portable build) and the quest log to edit. The editor reads a copy; the card is untouched so far.'),
            ('3.  Make changes.', 'Use the tabs, or start from a story preset. Revert throws away all edits.'),
            ('4.  Review changes.', 'Lists everything that will be written.'),
            ('5.  Write to card.', 'Choose the card and quest log to write into. You are shown what is there first, '
             'and a backup is kept next to the card as .before-craft.'),
            ('6.  Start BlueWake', 'and load that quest log.'),
        ]
        for r, (head, text) in enumerate(steps):
            ttk.Label(box, text=head, font=('', 10, 'bold')).grid(row=r * 2, column=0, sticky='w', pady=(6 if r else 0, 0))
            ttk.Label(box, text=text, wraplength=330, justify='left').grid(row=r * 2 + 1, column=0, sticky='w')
        ttk.Label(box, foreground='gray', wraplength=330, justify='left', text=(
            'Undo a write by copying the .before-craft file back over the card. Save a copy as .gci\u2026 '
            'keeps an edited save without touching any card. Restart place sets where the save starts; '
            'Story flags controls events and cutscenes, so change those with care.')).grid(
            row=len(steps) * 2, column=0, sticky='w', pady=(12, 0))

    def tab_presets(self, f):
        box = ttk.LabelFrame(f, text='Story preset', padding=6)
        box.grid(row=0, column=0, sticky='nw', padx=6, pady=4)
        self.presets = []
        self.preset_box = ttk.Combobox(box, width=48, state='readonly', postcommand=self.refresh_presets)
        self.preset_box.grid(row=0, column=0, sticky='w')
        ttk.Button(box, text='Apply', command=self.apply_preset).grid(row=0, column=1, padx=6)
        self.preset_mode = tk.StringVar(value='exact')
        ttk.Radiobutton(box, text='Exact copy of the preset save', variable=self.preset_mode,
                        value='exact').grid(row=1, column=0, columnspan=2, sticky='w')
        ttk.Radiobutton(box, text='Story progress only (experimental)', variable=self.preset_mode,
                        value='story').grid(row=2, column=0, columnspan=2, sticky='w')
        ttk.Label(box, foreground='gray', wraplength=470, justify='left', text=(
            'Exact copy replaces everything but the name and options. Story progress sets required items, '
            'equipment, songs, pearls, shards, story flags and dungeons to the preset, forwards or back, '
            'and keeps optional progress.')).grid(row=4, column=0, columnspan=2, sticky='w', pady=(4, 0))
        self.preset_note = ttk.Label(box, foreground='gray')
        self.preset_note.grid(row=3, column=0, columnspan=2, sticky='w')
        self.refresh_presets()
        self.preset = None

    def refresh_presets(self):
        """Re-read the presets each time the list opens, so new ones show up without a restart."""
        found, folder = [], None
        for folder in dict.fromkeys(PRESET_FOLDERS):
            found = wwedit.load_presets(folder)
            if found:
                break
        self.presets = found
        self.preset_box.config(values=[p['name'] for p in found])
        self.preset_note.config(text=f'{len(found)} preset{"s" if len(found) != 1 else ""} from {folder}' if found else
                                'No presets found in ' + ' and '.join(dict.fromkeys(PRESET_FOLDERS)) +
                                ' (tools/make_presets.py creates them).')

    def apply_preset(self):
        if not self.save:
            return messagebox.showinfo('Story preset', 'Open a save first.')
        i = self.preset_box.current()
        if i < 0:
            return
        p = self.presets[i]
        try:
            current, earlier = self.build_save()     # the save as it is now, with any edits so far
        except ValueError as error:
            return messagebox.showerror('Story preset', f'Check the values: {error}')
        if self.preset_mode.get() == 'exact':
            if not messagebox.askyesno('Story preset', f'Replace this save with: {p["name"]}?\n\nEverything but '
                                       'the name and options is replaced. Nothing is written until you write '
                                       'to a card or save a copy.'):
                return
            quest = wwedit.preset_quest(p, current)
            earlier = []
        else:
            quest, done = wwedit.preset_story_only(p, current, mandatory_flag)
            if not messagebox.askyesno('Story preset', f'Set this save\'s story progress to: {p["name"]}?\n\n'
                                       + '\n'.join(f'\u2022 {d}' for d in done[:25])
                                       + ('\n\u2026' if len(done) > 25 else '')
                                       + '\n\nOptional progress is kept. Nothing is written until you write '
                                       'to a card or save a copy.'):
                return
        s = wwedit.Save(self.source_path, int(self.slot_box.get()))
        s.q = bytearray(quest)
        mode = 'story progress' if self.preset_mode.get() == 'story' else 'exact copy'
        earlier = [c for c in earlier if not c.startswith('story preset')]
        self.preset = (f'{p["name"]} ({mode})', quest, earlier)
        self.populate(s)
        self.say(f'Applied the preset "{p["name"]}". Further edits apply on top of it.')

    def tab_status(self, f):
        health = ttk.LabelFrame(f, text='Health', padding=8)
        health.grid(row=0, column=0, sticky='nw', padx=6, pady=4)
        self.containers = tk.Spinbox(health, from_=1, to=20, width=6, command=self.update_total)
        self.pieces = tk.Spinbox(health, from_=0, to=3, width=6, command=self.update_total)
        for w in (self.containers, self.pieces):
            w.bind('<KeyRelease>', lambda e: self.update_total())
        self.hearts = tk.Spinbox(health, values=('3',), width=8, state='readonly')
        for r, (t, w) in enumerate([('Heart containers (whole hearts)', self.containers),
                                    ('Heart pieces toward the next', self.pieces),
                                    ('Current health (hearts)', self.hearts)]):
            ttk.Label(health, text=t).grid(row=r, column=0, sticky='w', pady=2)
            w.grid(row=r, column=1, sticky='w', padx=8)
        self.total = ttk.Label(health, foreground='gray')
        self.total.grid(row=3, column=0, columnspan=2, sticky='w', pady=(6, 0))
        money = ttk.LabelFrame(f, text='Rupees', padding=8)
        money.grid(row=0, column=1, sticky='nw', padx=6, pady=4)
        self.rupees = tk.Spinbox(money, from_=0, to=200, width=8)
        self.rupees.grid(row=0, column=0, sticky='w')
        self.wallet = tk.IntVar()
        for i, w in enumerate(WALLETS):
            ttk.Radiobutton(money, text=f'Wallet: {w}', variable=self.wallet, value=i,
                            command=self.cap_rupees).grid(row=i + 1, column=0, sticky='w')
        self.magic = tk.IntVar()
        self.radios(f, 'Magic meter', self.magic, MAGIC, 0, 2)

    @staticmethod
    def quarters_text(q):
        whole, part = divmod(q, 4)
        frac = ('', '\u00bc', '\u00bd', '\u00be')[part]
        return (f'{whole}' if whole else '') + frac    # no spaces: Tk splits list values on them

    def cap_rupees(self):
        top = int(WALLETS[self.wallet.get()])
        self.rupees.config(to=top)
        try:
            if int(self.rupees.get()) > top:
                self.set_spin(self.rupees, top)
        except ValueError:
            self.set_spin(self.rupees, 0)

    def update_total(self, current=None):
        """Keep pieces and current health consistent with the maximum."""
        try:
            c, p = int(self.containers.get()), int(self.pieces.get())
        except ValueError:
            return
        c = max(1, min(c, 20))
        if c == 20 and p:
            p = 0
            self.set_spin(self.pieces, 0)
        top = c * 4 + p
        if current is None:
            current = self.current_quarters()
        current = top if current is None else max(1, min(current, top))
        self.hearts.config(state='normal', values=tuple(self.quarters_text(q) for q in range(1, top + 1)))
        self.set_spin(self.hearts, self.quarters_text(current))
        self.hearts.config(state='readonly')
        self.total.config(text=f'Maximum health: {self.quarters_text(top)} hearts (game limit 20)')

    def current_quarters(self):
        text = self.hearts.get().strip()
        if not text:
            return None
        frac = {'\u00bc': 1, '\u00bd': 2, '\u00be': 3}.get(text[-1], 0)
        whole = text[:-1] if frac else text
        return (int(whole) if whole else 0) * 4 + frac

    def tab_items(self, f):
        toggles = ttk.LabelFrame(f, text='Items', padding=6)
        toggles.grid(row=0, column=0, rowspan=3, sticky='nw', padx=6, pady=4)
        self.toggle_vars = {}
        for i, name in enumerate(TOGGLES):
            v = tk.BooleanVar()
            ttk.Checkbutton(toggles, text=name, variable=v).grid(row=i % 7, column=i // 7, sticky='w', padx=(0, 12))
            self.toggle_vars[name] = v
        self.picto, self.bow, self.quiver, self.bombs = tk.StringVar(), tk.StringVar(), tk.IntVar(), tk.IntVar()
        self.radios(f, 'Picto Box', self.picto, [(p, p) for p in PICTO], 0, 1)
        self.radios(f, 'Bow', self.bow, [(b, b) for b in BOWS], 0, 2)
        self.radios(f, 'Quiver', self.quiver, [(str(c), c) for c in wwedit.CAPACITIES[1:]], 1, 2)
        self.radios(f, 'Bombs', self.bombs, [('none', 0)] + [(f'bag of {c}', c) for c in wwedit.CAPACITIES[1:]], 1, 1)
        bottles = ttk.LabelFrame(f, text='Bottles', padding=6)
        bottles.grid(row=3, column=0, columnspan=3, sticky='nw', padx=6, pady=4)
        self.bottle_boxes = []
        for i in range(4):
            box = ttk.Combobox(bottles, width=18, state='readonly', values=[b[0] for b in wwedit.BOTTLE_CONTENTS])
            box.grid(row=0, column=i, padx=4)
            self.bottle_boxes.append(box)
        ttk.Label(f, foreground='gray', text='Items are given the way the game gives them, including '
                  'starting arrows, bombs and magic.').grid(
            row=4, column=0, columnspan=3, sticky='w', pady=(8, 0))

    def tab_equipment(self, f):
        self.equip_vars = []
        for i, (name, options) in enumerate(wwedit.EQUIPMENT):
            v = tk.StringVar()
            self.radios(f, name, v, [(o[0], o[0]) for o in options], 0, i)
            self.equip_vars.append(v)

    def tab_bags(self, f):
        spoils = ttk.LabelFrame(f, text='Spoils Bag (count, 0 = none)', padding=6)
        spoils.grid(row=0, column=0, sticky='nw', padx=6)
        self.spoil_spins = {}
        for r, (name, _) in enumerate(wwedit.SPOILS):
            ttk.Label(spoils, text=name).grid(row=r, column=0, sticky='w')
            s = tk.Spinbox(spoils, from_=0, to=99, width=4)
            s.grid(row=r, column=1, padx=6, pady=1)
            self.spoil_spins[name] = s
        bait = ttk.LabelFrame(f, text='Bait Bag (3 bait per slot)', padding=6)
        bait.grid(row=0, column=1, sticky='nw', padx=6)
        self.bait_rows = []
        for r in range(8):
            box = ttk.Combobox(bait, width=16, state='readonly', values=[b[0] for b in wwedit.BAITS])
            box.grid(row=r, column=0, pady=1)
            s = tk.Spinbox(bait, from_=1, to=3, width=3)
            s.grid(row=r, column=1, padx=6)
            box.bind('<<ComboboxSelected>>', lambda e, b=box, sp=s: self.bait_count_state(b, sp))
            self.bait_rows.append((box, s))
        chart = ttk.LabelFrame(f, text='Sea chart', padding=6)
        chart.grid(row=0, column=3, sticky='nw', padx=6)
        self.chart_info = ttk.Label(chart)
        self.chart_info.grid(row=0, column=0, sticky='w')
        self.chart_mode = tk.StringVar(value='keep')
        for r, (text, value) in enumerate([('Keep as it is', 'keep'),
                                           ('Reveal every square', 'reveal'),
                                           ('Only the starting squares', 'reset')]):
            ttk.Radiobutton(chart, text=text, variable=self.chart_mode, value=value).grid(
                row=r + 1, column=0, sticky='w')
        ttk.Label(chart, foreground='gray', wraplength=200, justify='left', text=(
            'Revealing works on any save. Starting squares clears the ones fishmen drew too.')).grid(
            row=4, column=0, sticky='w', pady=(4, 0))
        delivery = ttk.LabelFrame(f, text='Delivery Bag (up to 8)', padding=6)
        delivery.grid(row=0, column=2, sticky='nw', padx=6)
        self.delivery_vars, self.delivery_checks = {}, {}
        for i, (name, _) in enumerate(wwedit.DELIVERY):
            v = tk.BooleanVar()
            c = ttk.Checkbutton(delivery, text=name, variable=v, command=self.update_delivery)
            c.grid(row=i % 10, column=i // 10, sticky='w', padx=(0, 8))
            self.delivery_vars[name], self.delivery_checks[name] = v, c
        self.delivery_count = ttk.Label(delivery, foreground='gray')
        self.delivery_count.grid(row=10, column=0, columnspan=2, sticky='w', pady=(6, 0))

    def update_delivery(self):
        """The bag has 8 slots: once 8 are chosen, the rest are greyed out."""
        chosen = sum(v.get() for v in self.delivery_vars.values())
        for name, c in self.delivery_checks.items():
            c.state(['!disabled'] if chosen < 8 or self.delivery_vars[name].get() else ['disabled'])
        self.delivery_count.config(text=f'{chosen} of 8 slots used')

    def bait_count_state(self, box, spin):
        """All-Purpose Bait is a stack (1-9); a Hyoi Pear is one item, so no count."""
        if box.get() == 'All-Purpose Bait':
            spin.config(state='normal')
            if not spin.get().isdigit() or not 1 <= int(spin.get()) <= 3:
                self.set_spin(spin, 3)
        else:
            spin.config(state='normal')
            self.set_spin(spin, '')
            spin.config(state='disabled')

    def tab_quest(self, f):
        self.song_vars = [tk.BooleanVar() for _ in wwedit.SONG_NAMES]
        self.pearl_vars = [tk.BooleanVar() for _ in wwedit.PEARL_NAMES]
        songs = ttk.LabelFrame(f, text='Songs', padding=6)
        songs.grid(row=0, column=0, rowspan=2, sticky='nw', padx=6)
        for i, (n, v) in enumerate(zip(wwedit.SONG_NAMES, self.song_vars)):
            ttk.Checkbutton(songs, text=n, variable=v).grid(row=i, column=0, sticky='w')
        pearls = ttk.LabelFrame(f, text='Pearls', padding=6)
        pearls.grid(row=0, column=1, sticky='nw', padx=6)
        for i, (n, v) in enumerate(zip(wwedit.PEARL_NAMES, self.pearl_vars)):
            ttk.Checkbutton(pearls, text=n, variable=v).grid(row=i, column=0, sticky='w')
        other = ttk.LabelFrame(f, text='Other', padding=6)
        other.grid(row=1, column=1, sticky='nw', padx=6, pady=6)
        self.charm = tk.BooleanVar()
        ttk.Checkbutton(other, text="Hero's Charm", variable=self.charm).grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(other, text='Triforce shards').grid(row=1, column=0, sticky='w', pady=(6, 0))
        self.shards = tk.Spinbox(other, from_=0, to=8, width=4)
        self.shards.grid(row=1, column=1, sticky='w', padx=6, pady=(6, 0))

    def tab_restart(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text='Restart place')
        self.restart_mode = tk.StringVar(value='keep')
        self.current_restart = ttk.Label(f)
        ttk.Radiobutton(f, text='Keep the current restart place', variable=self.restart_mode, value='keep',
                        command=self.restart_widgets).grid(row=0, column=0, sticky='w')
        self.current_restart.grid(row=0, column=1, sticky='w', padx=8)
        ttk.Radiobutton(f, text='A known spot', variable=self.restart_mode, value='spot',
                        command=self.restart_widgets).grid(row=1, column=0, sticky='w', pady=(8, 0))
        self.spot_box = ttk.Combobox(f, width=60, state='disabled', values=[s[0] for s in ALL_SPOTS])
        self.spot_box.grid(row=1, column=1, sticky='w', padx=8, pady=(8, 0))
        ttk.Radiobutton(f, text='Custom (advanced)', variable=self.restart_mode, value='custom',
                        command=self.restart_widgets).grid(row=2, column=0, sticky='w', pady=(8, 0))
        custom = ttk.Frame(f)
        custom.grid(row=2, column=1, sticky='w', padx=8, pady=(8, 0))
        # Stage, room and spawn point are all chosen from what is on the disc.
        self.stage = ttk.Combobox(custom, width=40, state='readonly')
        self.experimental = tk.BooleanVar()
        self.experimental_box = ttk.Checkbutton(
            custom, text='Also show unused, unknown and cutscene-only stages (experimental)',
            variable=self.experimental, command=self.fill_stages)
        self.experimental_box.grid(row=3, column=0, columnspan=2, sticky='w', pady=(6, 0))
        self.room = ttk.Combobox(custom, width=5, state='readonly')
        self.stage.bind('<<ComboboxSelected>>', lambda e: self.fill_rooms())
        self.room.bind('<<ComboboxSelected>>', lambda e: self.check_custom())
        self.point = ttk.Combobox(custom, width=34)
        for i, (t, w) in enumerate([('Stage', self.stage), ('Room', self.room), ('Spawn point', self.point)]):
            ttk.Label(custom, text=t).grid(row=i, column=0, sticky='w', pady=2)
            w.grid(row=i, column=1, sticky='w', padx=6, pady=2)
        ttk.Label(f, foreground='gray', wraplength=760, justify='left', text=(
            'Known spots are spawn points the game itself uses (from your saves and the Wind Waker '
            'Randomizer\'s entrance data), so they are safe. A custom place is checked against the disc '
            'for the stage and room, and its spawn points are read from that room\'s data, so only '
            'points the game can actually find are offered (a missing one freezes the game on load). '
            'Either way only the new copy is affected.')).grid(
            row=3, column=0, columnspan=2, sticky='w', pady=(16, 0))
        self.restart_widgets()

    def restart_widgets(self):
        mode = self.restart_mode.get()
        self.spot_box.config(state='readonly' if mode == 'spot' else 'disabled')
        for w in (self.stage, self.room, self.point):
            w.config(state='readonly' if mode == 'custom' else 'disabled')
        self.experimental_box.state(['!disabled'] if mode == 'custom' else ['disabled'])
        if mode == 'custom' and not self.stage.cget('values'):
            self.fill_stages()

    def fill_stages(self):
        iso, index = self.find_disc()
        stages = sorted(wwedit.disc_rooms(iso, index)) if iso else sorted(STAGE_NAMES)
        if not self.experimental.get():
            stages = [s for s in stages if not stage_experimental(s)]
        self.stage.config(values=[stage_label(s) + ('  [experimental]' if stage_experimental(s) else '')
                                  for s in stages])
        if self.stage_name() not in stages:
            self.stage.set('')
            self.room.config(values=[])
            self.room.set('')
            self.point.set('')

    def stage_name(self):
        return self.stage.get().split(' \u2014 ')[0].split('  [')[0].strip()

    def fill_rooms(self):
        iso, index = self.find_disc()
        if not iso:
            return
        rooms = sorted(wwedit.disc_rooms(iso, index).get(self.stage_name(), ()))
        self.room.config(values=[str(r) for r in rooms])
        self.room.set(str(rooms[0]) if rooms else '')
        self.point.set('')
        if rooms:
            self.check_custom()

    def find_disc(self):
        """(iso path, file index) for the game disc, or (None, {}) if none is found."""
        if getattr(self, 'disc', None) is None:
            iso = config.disc()
            self.disc = (iso, wwedit.disc_index(iso)) if iso else (None, {})
        return self.disc

    def check_custom(self, quiet=False):
        """List the spawn points for the custom stage/room; True if the chosen one exists."""
        iso, index = self.find_disc()
        stage = self.stage_name()
        if not iso:
            if not quiet:
                messagebox.showwarning('Restart place', 'No game disc image found to check against.')
            return None
        rooms = wwedit.disc_rooms(iso, index)
        if stage not in rooms:
            near = ', '.join(sorted(s for s in rooms if s.lower().startswith(stage[:3].lower()))[:12])
            messagebox.showerror('Restart place', f'There is no stage "{stage}" on the disc.' +
                                 (f'\nSimilar names: {near}' if near else ''))
            return False
        try:
            room = int(self.room.get())
        except ValueError:
            room = None
        if room not in rooms[stage]:
            messagebox.showerror('Restart place', f'Stage "{stage}" has no room {room}.\nRooms on the disc: '
                                 + ', '.join(map(str, sorted(rooms[stage]))))
            return False
        self.say(f'Reading the spawn points of {stage} room {room} from the disc...')
        spawns = wwedit.spawn_points(iso, stage, room, index)
        found = spawns['room'] or spawns['stage']
        where = 'room' if spawns['room'] else 'stage'
        if not found:
            messagebox.showerror('Restart place', f'{stage} room {room} has no spawn points.')
            return False
        values = [f'{sid}  (room {r}, x {x:.0f}, z {z:.0f})' for sid, r, x, y, z in found]
        self.point.config(values=values)
        current = self.point.get().split()[0] if self.point.get().split() else ''
        ids = {str(e[0]) for e in found}
        self.say(f'{len(found)} spawn points in the {where} data of {stage} room {room}.')
        if current not in ids:
            if quiet:
                messagebox.showerror('Restart place', f'Spawn point {current or "(none)"} does not exist in '
                                     f'{stage} room {room}; the game would freeze. Choose one from the list.')
                return False
            self.point.set(values[0])
        return True

    def restart_choice(self):
        mode = self.restart_mode.get()
        if mode == 'spot' and self.spot_box.current() >= 0:
            _, stage, room, point = ALL_SPOTS[self.spot_box.current()]
            return (stage, room, point)
        if mode == 'custom':
            return (self.stage_name(), int(self.room.get()), int(self.point.get().split()[0]))
        return None

    def tab_flags(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text='Story flags')
        bar = ttk.Frame(f)
        bar.pack(fill='x')
        ttk.Label(bar, text='Search').pack(side='left')
        self.search = ttk.Entry(bar, width=28)
        self.search.pack(side='left', padx=6)
        self.search.bind('<KeyRelease>', lambda e: self.fill_flags())
        ttk.Label(bar, text='Area').pack(side='left', padx=(10, 4))
        self.area = ttk.Combobox(bar, width=30, state='readonly', values=FLAG_AREA_NAMES)
        self.area.set('All areas')
        self.area.pack(side='left')
        self.area.bind('<<ComboboxSelected>>', lambda e: self.fill_flags())
        ttk.Label(bar, text='Show').pack(side='left', padx=(10, 4))
        self.show = ttk.Combobox(bar, width=12, state='readonly',
                                 values=['all', 'on', 'off', 'changed'])
        self.show.set('all')
        self.show.pack(side='left')
        self.show.bind('<<ComboboxSelected>>', lambda e: self.fill_flags())
        ttk.Button(bar, text='Turn on', command=lambda: self.set_selected(True)).pack(side='right')
        ttk.Button(bar, text='Turn off', command=lambda: self.set_selected(False)).pack(side='right', padx=6)
        cols = ('flag', 'state', 'area', 'about')
        table = ttk.Frame(f)
        table.pack(fill='both', expand=True, pady=6)
        self.tree = ttk.Treeview(table, columns=cols, show='headings', selectmode='extended')
        self.sort = ('flag', False)
        for c, w in zip(cols, (70, 60, 190, 560)):
            self.tree.heading(c, text=c.capitalize(), command=lambda c=c: self.sort_by(c))
            self.tree.column(c, width=w, stretch=(c == 'about'))
        scroll = ttk.Scrollbar(table, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', lambda e: self.toggle_selected())
        self.flag_count = ttk.Label(f, foreground='gray')
        self.flag_count.pack(anchor='w')
        ttk.Label(f, foreground='gray', text='Double-click toggles; click a column title to sort. Flags that differ '
                  'from the save as opened (including a preset\'s changes) are marked with *. Areas are a rough grouping by description. Descriptions: ZeldaSpeedRuns '
                  'sheet, Wind Waker Randomizer, zeldaret/tww decomp.', wraplength=900, justify='left').pack(anchor='w')

    def sort_by(self, column):
        col, reverse = self.sort
        self.sort = (column, not reverse if column == col else False)
        self.fill_flags()

    # ---------------------------------------------------------------- data
    def say(self, text):
        self.status.config(text=text)
        self.update_idletasks()

    # -------- sources: a catalog entry, any .gci, or a memory card (exported to a temporary .gci)
    def settings(self):
        try:
            return json.load(open(SETTINGS, encoding='utf-8'))
        except (OSError, ValueError):
            return {}

    def remember(self, **values):
        s = self.settings()
        s.update(values)
        try:
            json.dump(s, open(SETTINGS, 'w', encoding='utf-8'), indent=1)
        except OSError:
            pass

    def open_gci(self):
        path = filedialog.askopenfilename(title='Open a Wind Waker save (.gci)',
                                          filetypes=[('GameCube save', '*.gci'), ('All files', '*.*')])
        if path:
            self.source_path, self.source_label = path, os.path.basename(path)
            self.load()

    def open_card(self):
        start = os.path.dirname(self.card_path.get()) or os.path.expanduser('~')
        card = filedialog.askopenfilename(title='Open a BlueWake memory card', initialdir=start,
                                          filetypes=[('BlueWake card', '*.card'), ('All files', '*.*')])
        if not card:
            return
        tool = config.card_to_gci()
        if not tool:
            return messagebox.showerror('Open card', 'BlueWake\'s scripts/card_to_gci.py was not found. Add your '
                                        'BlueWake checkout to "bluewake_checkouts" in config.json.')
        self.say('Reading the card...')
        out = tempfile.mkdtemp(prefix='wwgui-card-')
        copy = os.path.join(out, 'GZLE01.card')
        shutil.copy2(card, copy)                      # read a copy, never the card itself
        result = subprocess.run([sys.executable, tool, copy, out], capture_output=True, text=True)
        gci = os.path.join(out, 'GZLE01-gczelda.gci')
        if result.returncode or not os.path.isfile(gci):
            return messagebox.showerror('Open card', 'No Wind Waker save found on that card.\n'
                                        + result.stdout + result.stderr)
        self.source_path, self.source_label = gci, os.path.basename(card)
        self.remember(card=card)
        self.load()

    def pick_card(self):
        start = os.path.dirname(self.card_path.get()) or os.path.expanduser('~')
        card = filedialog.askopenfilename(title='Card to write to', initialdir=start,
                                          filetypes=[('BlueWake card', '*.card'), ('All files', '*.*')])
        if card:
            self.card_path.delete(0, 'end')
            self.card_path.insert(0, card)
            self.remember(card=card)

    def load(self):
        try:
            s = wwedit.Save(self.source_path, int(self.slot_box.get()))
        except Exception as error:
            return messagebox.showerror('Load', str(error))
        if not s.name():
            self.save = None
            self.info.config(text=f'{self.source_label}: quest log {self.slot_box.get()} is empty.')
            return
        self.preset = None
        self.loaded = s                 # as opened, before any preset: what "changed" compares with
        self.populate(s)
        self.say('Loaded. Nothing changes until you write.')

    def populate(self, s):
        """Show a save on every tab; edits are measured against what is shown here."""
        self.save, self.flag_changes = s, {}
        self.say('Loading the flag descriptions...')
        wwcat.load_sheet()
        life_max = s.u16(wwedit.LIFE_MAX)
        self.set_spin(self.containers, life_max // 4)
        self.set_spin(self.pieces, life_max % 4)
        self.update_total(current=s.u16(wwedit.LIFE))
        self.set_spin(self.rupees, s.u16(wwedit.RUPEES))
        self.wallet.set(min(s.q[wwedit.WALLET], 2))
        self.rupees.config(to=int(WALLETS[self.wallet.get()]))
        self.magic.set(min((m for _, m in MAGIC), key=lambda m: abs(m - s.q[wwedit.MAGIC_MAX])))
        for n, v in self.toggle_vars.items():
            v.set(s.has(n))
        picto = s.q[wwedit.ITEMS + 8]
        self.picto.set({0x23: 'Picto Box', 0x26: 'Deluxe Picto Box'}.get(picto, 'none'))
        bow = s.q[wwedit.ITEMS + 12]
        self.bow.set({0x27: "Hero's Bow", 0x35: 'Fire and Ice Arrows', 0x36: 'Light Arrows'}.get(bow, 'none'))
        snap = lambda v, opts: min(opts, key=lambda c: abs(c - v))
        self.quiver.set(snap(s.q[wwedit.ARROWS_MAX] or 30, wwedit.CAPACITIES[1:]))
        has_bombs = s.q[wwedit.ITEMS + 13] == 0x31
        self.bombs.set(snap(s.q[wwedit.BOMBS_MAX] or 30, wwedit.CAPACITIES[1:]) if has_bombs else 0)
        for i, box in enumerate(self.bottle_boxes):
            box.set(s.bottle(i))
        for i, v in enumerate(self.equip_vars):
            v.set(s.equipment(i))
        counts = s.spoils()
        for n, spin in self.spoil_spins.items():
            self.set_spin(spin, counts.get(n, 0))
        for (box, spin), (n, c) in zip(self.bait_rows, s.bait()):
            box.set(n)
            spin.config(state='normal')
            self.set_spin(spin, min(max(c, 1), 3))
            self.bait_count_state(box, spin)
        self.chart_mode.set('keep')
        self.chart_info.config(text=f'{s.chart_drawn()} of 49 squares drawn')
        held = s.delivery()
        for n, v in self.delivery_vars.items():
            v.set(n in held)
        self.update_delivery()
        for v, on in zip(self.song_vars, s.bits(wwedit.SONGS)):
            v.set(on)
        for v, on in zip(self.pearl_vars, s.bits(wwedit.PEARLS)):
            v.set(on)
        self.charm.set(bool(s.q[wwedit.HEROS_CHARM] & 1))
        self.set_spin(self.shards, sum(s.bits(wwedit.SHARDS)))
        stage, room, point = s.restart()
        self.current_restart.config(text=f'({stage_label(stage)}, room {room}, spawn point {point})')
        self.restart_mode.set('keep')
        self.spot_box.set('')
        self.restart_widgets()
        self.stage.set(stage_label(stage))
        self.room.set(str(room))
        self.point.set(str(point))
        self.restart_widgets()
        self.initial = self.read_widgets()
        self.fill_flags()
        preset = f', preset: {self.preset[0]}' if self.preset else ''
        self.info.config(text=f'{self.source_label}, quest log {self.slot_box.get()}: {s.name()}, checksums '
                              f'{"ok" if s.checksum_ok() else "BAD"}{preset}')

    @staticmethod
    def set_spin(spin, value):
        spin.delete(0, 'end')
        spin.insert(0, f'{value:g}' if isinstance(value, float) else str(value))

    def read_widgets(self):
        return {
            'life': (int(self.containers.get()), int(self.pieces.get()), self.current_quarters()),
            'rupees': int(self.rupees.get()), 'wallet': self.wallet.get(), 'magic': self.magic.get(),
            'toggles': {n: v.get() for n, v in self.toggle_vars.items()},
            'picto': self.picto.get(), 'bow': self.bow.get(), 'quiver': self.quiver.get(),
            'bombs': self.bombs.get(), 'bottles': [b.get() for b in self.bottle_boxes],
            'equipment': [v.get() for v in self.equip_vars],
            'spoils': {n: int(s.get()) for n, s in self.spoil_spins.items()},
            'bait': [(b.get(), int(s.get()) if b.get() == 'All-Purpose Bait' else 0) for b, s in self.bait_rows],
            'delivery': sorted(n for n, v in self.delivery_vars.items() if v.get()),
            'songs': [v.get() for v in self.song_vars], 'pearls': [v.get() for v in self.pearl_vars],
            'charm': self.charm.get(), 'shards': int(self.shards.get()), 'chart': self.chart_mode.get(),
            'restart': self.restart_choice(),
        }

    def flag_on(self, v):
        return self.flag_changes.get(v, self.save.flag(v))

    def fill_flags(self):
        if not self.save:
            return
        self.tree.delete(*self.tree.get_children())
        words = self.search.get().lower().split()
        area_wanted, show = self.area.get(), self.show.get()
        rows = []
        for v, name, comment in wwcat.FLAG_BITS:
            on = self.flag_on(v)
            changed = on != self.loaded.flag(v)
            if (show == 'on' and not on) or (show == 'off' and on) or (show == 'changed' and not changed):
                continue
            about = wwcat.describe_flag(v, name, comment)
            area = flag_area(about)
            if area_wanted != 'All areas' and area != area_wanted:
                continue
            if words and not all(w in f'0x{v:04X} {about} {area}'.lower() for w in words):
                continue
            mark = '*' if changed else ''
            rows.append((v, ('on' if on else 'off') + mark, area, about))
        col, reverse = self.sort
        key = {'flag': lambda r: r[0], 'state': lambda r: (r[1], r[0]),
               'area': lambda r: (FLAG_AREA_NAMES.index(r[2]), r[0]), 'about': lambda r: (r[3].lower(), r[0])}[col]
        rows.sort(key=key, reverse=reverse)
        for v, state, area, about in rows:
            self.tree.insert('', 'end', iid=str(v), values=(f'0x{v:04X}', state, area, about))
        for c in ('flag', 'state', 'area', 'about'):
            arrow = (' \u25bc' if reverse else ' \u25b2') if c == col else ''
            self.tree.heading(c, text=c.capitalize() + arrow)
        self.flag_count.config(text=f'{len(rows)} flags shown, {sum(1 for r in rows if r[1].startswith("on"))} on.')

    def set_selected(self, on):
        for iid in self.tree.selection():
            v = int(iid)
            if on == self.save.flag(v):
                self.flag_changes.pop(v, None)
            else:
                self.flag_changes[v] = on
        self.fill_flags()

    def toggle_selected(self):
        for iid in self.tree.selection():
            v = int(iid)
            self.set_selected_one(v, not self.flag_on(v))
        self.fill_flags()

    def set_selected_one(self, v, on):
        if on == self.save.flag(v):
            self.flag_changes.pop(v, None)
        else:
            self.flag_changes[v] = on

    # ---------------------------------------------------------------- saving
    def build_save(self):
        """Apply what changed on the tabs to a fresh copy of the loaded quest log."""
        s = wwedit.Save(self.source_path, int(self.slot_box.get()))
        now, was, changes = self.read_widgets(), self.initial, []
        if self.preset:
            s.q = bytearray(self.preset[1])
            changes.append(f'story preset: {self.preset[0]}')
            changes += self.preset[2]
        if now['life'] != was['life']:
            c, p, h = now['life']
            top = min(c * 4 + p, 80)
            s.set_u16(wwedit.LIFE_MAX, top)
            s.set_u16(wwedit.LIFE, min(h, top))
            changes.append(f'health {self.quarters_text(min(h, top))} of {self.quarters_text(top)} hearts')
        if now['wallet'] != was['wallet']:
            s.set_wallet(now['wallet'])
            changes.append(f'wallet {WALLETS[now["wallet"]]}')
        if now['rupees'] != was['rupees'] or now['wallet'] != was['wallet']:
            s.set_rupees(min(now['rupees'], int(WALLETS[now['wallet']])))
            changes.append(f'rupees {now["rupees"]}')
        if now['magic'] != was['magic']:
            s.q[wwedit.MAGIC_MAX] = s.q[wwedit.MAGIC] = now['magic']
            changes.append(f'magic {now["magic"]}')
        for n, on in now['toggles'].items():
            if on != was['toggles'][n]:
                if on:
                    s.give(n)
                else:
                    s.take(wwedit.ITEMS_GIVEN[n][0])
                changes.append(f'{"gave" if on else "removed"} {n}')
        for key, slot in (('picto', 8), ('bow', 12)):
            if now[key] != was[key]:
                if now[key] == 'none':
                    s.take(slot)
                else:
                    s.give(now[key])
                changes.append(f'{key}: {now[key]}')
        if now['quiver'] != was['quiver'] or (was['bow'] == 'none' and now['bow'] != 'none'):
            s.set_quiver(now['quiver'])
            changes.append(f'quiver {now["quiver"]}')
        if now['bombs'] != was['bombs']:
            s.set_bombs(now['bombs'])
            changes.append(f'bombs {now["bombs"] or "none"}')
        for i, b in enumerate(now['bottles']):
            if b != was['bottles'][i]:
                s.set_bottle(i, b)
                changes.append(f'bottle {i + 1}: {b}')
        for i, name in enumerate(now['equipment']):
            if name != was['equipment'][i]:
                s.set_equipment(i, name)
                changes.append(f'{wwedit.EQUIPMENT[i][0].lower()}: {name}')
        if now['spoils'] != was['spoils']:
            s.set_spoils(now['spoils'])
            changes.append('spoils: ' + (', '.join(f'{n} {c}' for n, c in now['spoils'].items() if c) or 'empty'))
        if now['bait'] != was['bait']:
            s.set_bait(now['bait'])
            changes.append('bait: ' + (', '.join(f'{n} {c}' if n == 'All-Purpose Bait' else n
                                                 for n, c in now['bait'] if n != 'none') or 'empty'))
        if now['delivery'] != was['delivery']:
            s.set_delivery(now['delivery'])
            changes.append('delivery bag: ' + (', '.join(now['delivery']) or 'empty'))
        if now['songs'] != was['songs']:
            before = s.q[wwedit.SONGS]
            s.set_bits(wwedit.SONGS, now['songs'])
            wwedit.sync_song_flags(s, before)
            changes.append('songs: ' + (', '.join(n for n, on in zip(wwedit.SONG_NAMES, now['songs']) if on) or 'none'))
        if now['pearls'] != was['pearls']:
            s.set_bits(wwedit.PEARLS, now['pearls'])
            changes.append('pearls: ' + (', '.join(n for n, on in zip(wwedit.PEARL_NAMES, now['pearls']) if on) or 'none'))
        if now['charm'] != was['charm']:
            s.q[wwedit.HEROS_CHARM] = (s.q[wwedit.HEROS_CHARM] & 0xFE) | int(now['charm'])
            changes.append(f"Hero's Charm {'on' if now['charm'] else 'off'}")
        if now['shards'] != was['shards']:
            s.set_bits(wwedit.SHARDS, [i < now['shards'] for i in range(8)])
            changes.append(f'Triforce shards {now["shards"]}')
        if now['chart'] != 'keep':
            s.set_chart(now['chart'])
            changes.append('sea chart: ' + ('every square drawn' if now['chart'] == 'reveal' else 'starting squares only'))
        if now['restart'] is not None:
            s.set_restart(*now['restart'])
            changes.append('restart {} {} {}'.format(*now['restart']))
        for v, on in sorted(self.flag_changes.items()):
            s.set_flag(v, on)
            changes.append(f'flag 0x{v:04X} {"on" if on else "off"}')
        return s, changes

    def review(self):
        if not self.save:
            return messagebox.showinfo('Review', 'Load a save first.')
        try:
            _, changes = self.build_save()
        except ValueError as error:
            return messagebox.showerror('Review', f'Check the values: {error}')
        messagebox.showinfo('Review', '\n'.join(f'\u2022 {c}' for c in changes) or 'Nothing has changed yet.')

    def finish(self, mode):
        """mode 'card': write into the chosen card; 'copy': save a .gci where you choose."""
        if not self.save:
            return messagebox.showinfo('Save', 'Load a save first.')
        if self.restart_mode.get() == 'custom' and self.check_custom(quiet=True) is False:
            return
        try:
            s, changes = self.build_save()
        except ValueError as error:
            return messagebox.showerror('Save', f'Check the values: {error}')
        if not changes and not messagebox.askyesno('Save', 'Nothing has changed. Save it anyway?'):
            return
        if mode == 'card':
            card, target = self.card_path.get().strip(), self.target_slot.get()
            if not os.path.isfile(card):
                return messagebox.showerror('Card', 'Choose a card to write to (Browse\u2026).')
            if not os.path.isfile(INJECT):
                return messagebox.showerror('Card', f'{INJECT} is missing.')
            shown = subprocess.run([INJECT, 'show', card], capture_output=True, text=True).stdout.strip()
            if not messagebox.askyesno('Write to card', f'Write this save into quest log {target} of\n{card}?\n\n'
                                       f'The card now holds:\n{shown or "(could not read it)"}\n\n'
                                       'A backup is kept next to it as .before-craft.'):
                return
            gci = os.path.join(tempfile.mkdtemp(prefix='wwgui-write-'), 'GZLE01-gczelda.gci')
            s.save(gci)
            shutil.copy2(card, card + '.before-craft')
            result = subprocess.run([INJECT, 'inject', card, gci, self.slot_box.get(), target, card],
                                    capture_output=True, text=True)
            if result.returncode:
                return messagebox.showerror('Card', f'Writing to the card failed:\n{result.stdout}{result.stderr}')
            self.remember(card=card)
            msg = f'Written to quest log {target} of the card ({len(changes)} change(s)); backup kept as .before-craft.'
        else:
            path = filedialog.asksaveasfilename(title='Save a copy', defaultextension='.gci',
                                                initialfile='GZLE01-gczelda.gci',
                                                filetypes=[('GameCube save', '*.gci')])
            if not path:
                return
            s.save(path)
            gci = path
            msg = f'Saved {path} ({len(changes)} change(s)).'
        self.say(msg)

if __name__ == '__main__':
    App().mainloop()
