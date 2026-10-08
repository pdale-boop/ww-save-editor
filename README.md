# Wind Waker save editor for BlueWake

A save editor for *The Legend of Zelda: The Wind Waker* (GameCube, USA, `GZLE01`), made for
[BlueWake](https://github.com/chrissotraidis/bluewake)'s memory cards. Open a card, change your
items, equipment, songs, bags, restart place or story flags, or jump to a point in the story, then
write the save back.

Every change is modeled on what the game itself does, using the
[zeldaret/tww](https://github.com/zeldaret/tww) decompilation: giving an item runs the same steps
as the game's own pickup, restart places follow the game's spawn lookup, and the checksums are the
game's own.

## Features

- **Link:** heart containers and pieces (up to the game's limit of 20 hearts), current health,
  rupees and wallet, magic meter, sword, shield, bracelets, songs, pearls, Triforce shards and the
  Hero's Charm.
- **Inventory:** every item, Picto Box and bow levels, quiver and bomb bag sizes, bottles and their
  contents, and the Spoils, Bait and Delivery Bags.
- **Sea chart:** reveal every square on any save (like Better Wind Waker's option, which only
  works on new files), or reset it to a new file's.
- **Restart place:** where the save starts when loaded. Pick a known spot, or any stage and room on
  your disc; only spawn points that exist in that room are offered, since a missing one freezes the
  game.
- **Story flags:** all 487, with descriptions, grouped by area, searchable and sortable.
- **Story presets:** jump to a point in the story. Presets from a full playthrough are included.

## Requirements

- Python 3.10 or newer with Tk, which the window uses.
  - **Windows and macOS:** the installers from python.org include Tk.
  - **Linux:** install your distribution's Tk package as well, for example `python3-tk`.
- A [BlueWake](https://github.com/chrissotraidis/bluewake) source checkout, for its
  `scripts/card_to_gci.py` (reads cards) and the save injector source (writes cards).
- Optional: your game disc image, for checking custom restart places. BlueWake builds keep a copy
  in `build/.../BlueWake/game/`, which is found automatically.

BlueWake's memory card is found automatically:

| System | Card location |
|---|---|
| Windows | `%APPDATA%\BlueWake\GZLE01.card` |
| macOS | `~/Library/Application Support/BlueWake/GZLE01.card` |
| Linux | the macOS-style path if it exists, otherwise `~/.local/share/BlueWake/GZLE01.card` |

Portable builds keep their own card in the build's `user` folder; open it with *Open card…*. The
editor has been tested on Windows; the macOS and Linux locations come from BlueWake's source and
are untested.

## Setup

1. Clone this repository.
2. Build the save injector from your BlueWake checkout with any C compiler.

   **Windows** (the clang that comes with Visual Studio):
   ```
   cd C:\path\to\bluewake
   clang -std=c11 -O1 -o C:\path\to\ww-save-editor\bwinject.exe tests\dolphin_save_import_cli.c apple\ios\src\dolphin_save_import.c
   ```
   Two warnings about `fopen` are normal.

   **macOS and Linux:**
   ```
   cd ~/path/to/bluewake
   cc -std=c11 -O1 -o ~/path/to/ww-save-editor/bwinject tests/dolphin_save_import_cli.c apple/ios/src/dolphin_save_import.c
   ```
3. Copy `config.example.json` (or `config.example.macos.json`) to `config.json` and set
   `bluewake_checkouts` to your BlueWake checkout. Every other setting has a default; `config.py`
   lists them all.
4. Run `python wwgui.py` (`python3 wwgui.py` on macOS and Linux).

## Using the editor

1. **Close BlueWake.** It keeps the memory card open and could overwrite your changes when it
   saves.
2. **Open card…** and choose the quest log to edit. The editor reads a copy, so the card is not
   touched yet.
3. **Make changes** on the tabs, or apply a story preset. *Revert* discards all edits.
4. **Review changes** lists exactly what will be written. It also warns when story flags are out
   of the story's usual order, for example a later milestone on while an earlier one is off.
   The warnings never block anything, since a save can be out of order on purpose; saving asks
   first if your edits are what put it out of order.
5. **Write to card**, choosing the quest log to write into. You are shown what the card holds
   first, and a backup is kept next to it as `.before-craft`.
6. **Start BlueWake** and load that quest log.

To undo a write, copy the `.before-craft` file back over the card. *Save a copy as .gci…* keeps an
edited save without touching any card.

## Story presets

The `presets` folder holds reference saves from my own playthrough, at points across the whole
story, named in `presets/presets.json`. Pick one on the Link tab and press *Apply*. Your player
name and options are always kept.

There are two modes:

- **Exact copy** replaces everything else with the preset save: items, story flags, dungeon
  progress, the sea chart, rupees and hearts.
- **Story progress only** (experimental) sets just the story to that point, forwards or backwards:
  required items, equipment, songs, pearls, Triforce shards, story flags and dungeons. Optional
  progress stays as you have it: hearts, rupees, bags, bottles, side quests and optional items.
  Which story flags count as required is currently a judgment from the flag descriptions and needs
  more research, so check the list of changes it shows before applying.

The playthrough was made with Better Wind Waker's "Reveal full sea chart" option on, so exact-copy
presets come with the whole sea chart drawn. Use the sea chart option on the Inventory tab to reset
it. Each preset file is a complete save export; the editor only uses its first quest log.

To add your own presets from a save catalog, use `tools/make_presets.py`.

## Tested in the game

- Saves built from BlueWake save states match the game's own saves byte for byte, apart from the
  save time.
- An item given outside its normal place (the Grappling Hook before Dragon Roost) works in play.
- Clearing a story flag replays its event (the King of Red Lions' sail speech).
- Restart places, including the cause of freezes: asking for a spawn point that does not exist in
  the chosen room freezes the game on load (`sea 0 206` froze, while `sea 0 0` and `sea 44 206`
  loaded). A restart inside a boss room works too: `M_DragB 0 1` (Gohma) loads on safe ground
  with Gohma not yet spawned, and walking forward starts the boss cutscene.
- A save with the sea chart reset to a new file's.

## Research tools

The `tools` folder holds the command-line tools used to work out the save format from a full
playthrough's save states. They are interactive; run them with no arguments. They were written and
tested on Windows; `wwcat.py` in particular expects a Windows BlueWake build to open states in.

- `wwcat.py`: browse save states, open each in BlueWake, turn them into saves, label them, check them against
  saves the game made, and compare story flags between saves in story order.
- `craft.py`: a command-line version of the editor for quick test saves.
- `make_presets.py`: turn catalog entries into story presets. Use after wwcat.py.
- `vanilla_chart.py`: copy a save with its sea chart reset to a new file's.

## Credits and licenses

This project is licensed under the GNU GPL, version 3 (see `LICENSE`), the same as BlueWake.

- **[zeldaret/tww](https://github.com/zeldaret/tww)** decompilation (CC0): the save layout,
  offsets and game behaviour this editor follows.
- **[Wind Waker Randomizer](https://github.com/LagoLunatic/wwrando)** by LagoLunatic (MIT): item
  names, stage descriptions, entrance spawn points and flag notes. Its license is reproduced in
  `NOTICE`.
- **[ZeldaSpeedRuns](https://www.zeldaspeedruns.com/tww/general-knowledge/flags-and-triggers)**
  community flag spreadsheet: story flag descriptions, downloaded at runtime rather than included.
- **[BlueWake](https://github.com/chrissotraidis/bluewake)**: the memory card tools this editor
  relies on.

See `NOTICE` for details. *The Legend of Zelda: The Wind Waker* is © Nintendo. This project
contains no game code or assets; you need your own copy of the game.

## How this was made

Written with the help of an AI assistant (Claude, by Anthropic), directed and tested by me. Every
behaviour listed under "Tested in the game" was checked by playing the result in BlueWake.
