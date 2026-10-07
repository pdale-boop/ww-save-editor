# Wind Waker save editor: notes for Claude

A save editor for The Wind Waker (GameCube USA, `GZLE01` rev 0) as run by BlueWake, a static
recompilation. Python 3.10+ with Tk; no other dependencies. Read `README.md` for what it does and
`TODO.md` for what's next.

## Layout

- `wwedit.py`: the editing core. All save layout knowledge lives here: offsets, checksums, item
  pickups, bags, presets, disc reading (FST, Yaz0, RARC, `PLYR` spawn lists). No UI.
- `wwgui.py`: the Tk window on top of `wwedit.py`. Tabs: Link, Inventory, Restart place, Story
  flags. Edits are compared against what was loaded and only the differences are written.
- `config.py`: every path, with per-OS defaults, overridden by an untracked `config.json`.
- `tools/`: research tools. `wwcat.py` (save states → saves, flag timeline, flag descriptions),
  `craft.py`, `make_presets.py`, `vanilla_chart.py`. `wwgui.py` imports `tools/wwcat.py` for the
  flag tables and descriptions.
- `presets/`: reference saves from a full playthrough, named in `presets.json`.

## How saves work (essentials)

- A `.gci` is a 64-byte header plus 12 blocks of 0x2000. Blocks 1 and 2 each hold all three quest
  logs (0x770 each, starting 8 bytes into the block); edits go to both copies.
- A quest log is 0x768 bytes of packed save data (`dSv_save_c_PACKED` in the decomp) plus an
  8-byte checksum (byte sum and inverted byte sum). Each block ends with a 16-bit word checksum.
  `wwedit.Save.save()` recomputes all of them.
- In RAM the save is unpacked (different member offsets) at `0x803C4C08`; `tools/wwcat.py`
  converts RAM to card layout the way the game's `memory_to_card` does.
- Cards are BlueWake's own container, not Dolphin `.raw`. Reading goes through BlueWake's
  `scripts/card_to_gci.py`; writing through an injector built from BlueWake's
  `tests/dolphin_save_import_cli.c`. Replacing both with Python is on the TODO list.

## Rules

- Copy the game's behaviour, don't invent it. Every rule comes from the zeldaret/tww decomp
  (CC0) and should name its source function in a comment (for example `item_func_rope`,
  `dSv_player_get_item_c::onBottleItem`, `dStage_playerInit`). If the decomp doesn't settle
  something, say so in the code and in the UI rather than guessing silently.
- Never write to a user's card without a backup next to it (`.before-craft`) and a confirmation
  showing what's in the target quest log. Read cards through a temporary copy.
- Only offer values the game can produce or handle: health caps at 80 quarters (20 hearts,
  `dMeter_LifeMove`), bait stacks are 3 (`setBaitItem`), the Delivery Bag holds 8 of items
  0x8C–0x9E (0x9F is not a delivery item), restart spawn points must exist in the room's `PLYR`
  list (a missing one freezes the game on load; verified in game).
- Keep a fact's evidence level honest. The README's "Tested in the game" list only gets entries
  that were actually played in BlueWake. Untested platforms and experimental modes are labeled.
- Licensing: this project is GPLv3. Randomizer data (item names, stage names, entrances, flag
  notes) is MIT and its notice lives in `NOTICE`; keep it there when adding more. The
  ZeldaSpeedRuns flag sheet is downloaded at runtime and must not be committed.
- Tools are interactive: no command-line flags, prompts with defaults, plain status messages.

## Known traps

- Tk Spinbox and Combobox `values` are split on spaces: keep list values free of spaces (heart
  quarters are shown as `5¾`, not `5 ¾`).
- Windows drops trailing dots from folder names; sanitize names before creating folders.
- BlueWake keeps the card open while running and can overwrite edits when it saves.
- Items and story flags are separate. An item can be given without its story flag (the chest or
  NPC still offers it). Songs have "learned" flags that must follow the song (`SONG_FLAGS`).
- Save states made mid-event can hold half-updated flags; the catalog tags them `[mid-...]`.
- The flag areas in `wwgui.py` are keyword matches on descriptions. "Required" story flags for
  presets are a heuristic (`mandatory_flag`) pending real research (see TODO).

## Testing

There is no test suite yet. Check changes by:

- Building a save with the change, then reading it back with `wwedit.Save`: checksums must pass
  (`checksum_ok()`) and the edited fields must hold the new values.
- For anything that touches extraction, `tools/wwcat.py` option 2 compares a save built from a
  state with a save the game wrote from the same state: only the save time (status B) and
  checksum may differ.
- Opening `wwgui.py` and exercising the changed tab, including Review changes.
- Anything claimed to work in the game needs a BlueWake session: write to a test build's card
  (portable mode), load it, play.

## Git

Commit to `main` for small changes; use a branch and pull request for larger features. Commits
use the owner's GitHub noreply address; don't change git identity settings. Don't push or open
pull requests without being asked.
