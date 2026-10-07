r"""Where things are. Every path has a default; override any of them in config.json next to
this file (see config.example.json). Nothing here is specific to one computer.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))

DEFAULTS = {
    # A BlueWake source checkout (git clone). Used for scripts/card_to_gci.py, and its portable
    # builds' cards and disc images are offered automatically. Several can be listed.
    'bluewake_checkouts': [],
    # The save injector built from BlueWake's tests/dolphin_save_import_cli.c (see README).
    'inject': os.path.join(ROOT, 'bwinject.exe'),
    # Memory cards to offer. BlueWake's normal location is listed first.
    'cards': [os.path.join(APPDATA, 'BlueWake', 'GZLE01.card')],
    # The game disc image, for checking restart places. Found in checkouts' builds if empty.
    'disc': '',
    # Story presets and the research catalog.
    'presets': os.path.join(ROOT, 'presets'),
    'catalog': os.path.join(ROOT, 'catalog'),
    # Save states for the catalog tools (BlueWake writes them to %APPDATA%\BlueWake\states).
    'states': os.path.join(APPDATA, 'BlueWake', 'states'),
}


def load():
    settings = dict(DEFAULTS)
    try:
        with open(os.path.join(ROOT, 'config.json'), encoding='utf-8') as f:
            settings.update(json.load(f))
    except (OSError, ValueError):
        pass
    return settings


SETTINGS = load()


def checkouts():
    return [os.path.expandvars(c) for c in SETTINGS['bluewake_checkouts']]


def card_to_gci():
    """BlueWake's scripts/card_to_gci.py, or None."""
    for c in checkouts():
        path = os.path.join(c, 'scripts', 'card_to_gci.py')
        if os.path.isfile(path):
            return path
    return None


def cards():
    found = [os.path.expandvars(c) for c in SETTINGS['cards']]
    for c in checkouts():
        found += glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'user', 'GZLE01.card'))
    return [c for c in dict.fromkeys(found) if os.path.isfile(c)]


def bluewake_exes():
    exes = []
    for c in checkouts():
        exes += glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'BlueWake.exe'))
    return exes


def disc():
    if SETTINGS['disc'] and os.path.isfile(os.path.expandvars(SETTINGS['disc'])):
        return os.path.expandvars(SETTINGS['disc'])
    for c in checkouts():
        for iso in glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'game', '*.iso')):
            return iso
    return None


def path(key):
    return os.path.expandvars(SETTINGS[key])
