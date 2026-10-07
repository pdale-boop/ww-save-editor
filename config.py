r"""Where things are. Every path has a default for Windows, macOS and Linux; override any of
them in config.json next to this file (see config.example.json).
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WINDOWS = os.name == 'nt'
MAC = sys.platform == 'darwin'


def bluewake_data():
    """Where BlueWake keeps its card, settings and states on this system.

    Windows: %APPDATA%\\BlueWake (scripts/windows/build.py). macOS: ~/Library/Application Support/
    BlueWake (runtime/host/src/card_runtime.c). Linux builds were still new when this was written;
    the same Library path is BlueWake's fallback, and ~/.local/share/BlueWake is checked too.
    """
    if WINDOWS:
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'BlueWake')
    mac_style = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'BlueWake')
    if MAC or os.path.isdir(mac_style):
        return mac_style
    return os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'BlueWake')


DATA = bluewake_data()

DEFAULTS = {
    # A BlueWake source checkout (git clone). Used for scripts/card_to_gci.py, and its portable
    # builds' cards and disc images are offered automatically. Several can be listed.
    'bluewake_checkouts': [],
    # The save injector built from BlueWake's tests/dolphin_save_import_cli.c (see README).
    'inject': os.path.join(ROOT, 'bwinject.exe' if WINDOWS else 'bwinject'),
    # Memory cards to offer. BlueWake's normal location is listed first.
    'cards': [os.path.join(DATA, 'GZLE01.card')],
    # The game disc image, for checking restart places. Found in checkouts' builds if empty.
    'disc': '',
    # Story presets and the research catalog.
    'presets': os.path.join(ROOT, 'presets'),
    'catalog': os.path.join(ROOT, 'catalog'),
    # Save states for the catalog tools (Windows: states, macOS: States, inside BlueWake's folder).
    'states': os.path.join(DATA, 'states' if WINDOWS else 'States'),
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
    return [os.path.expanduser(os.path.expandvars(c)) for c in SETTINGS['bluewake_checkouts']]


def card_to_gci():
    """BlueWake's scripts/card_to_gci.py, or None."""
    for c in checkouts():
        path = os.path.join(c, 'scripts', 'card_to_gci.py')
        if os.path.isfile(path):
            return path
    return None


def cards():
    found = [os.path.expanduser(os.path.expandvars(c)) for c in SETTINGS['cards']]
    for c in checkouts():
        found += glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'user', 'GZLE01.card'))
    return [c for c in dict.fromkeys(found) if os.path.isfile(c)]


def bluewake_exes():
    exes = []
    for c in checkouts():
        exes += glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'BlueWake.exe' if WINDOWS else 'BlueWake'))
    return [e for e in exes if os.path.isfile(e)]


def disc():
    if SETTINGS['disc'] and os.path.isfile(path('disc')):
        return path('disc')
    for c in checkouts():
        for iso in glob.glob(os.path.join(c, 'build', '*', 'BlueWake', 'game', '*.iso')):
            return iso
    return None


def path(key):
    return os.path.expanduser(os.path.expandvars(SETTINGS[key]))
