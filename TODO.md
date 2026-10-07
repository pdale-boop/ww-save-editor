# To do

What's left for the Wind Waker save editor, roughly in order of value. Things marked
**(in game)** need a BlueWake session to check.

## Verify

- [ ] **(in game)** Story presets: apply an exact-copy preset, write it to a card, load it and
      play for a few minutes. Then the same with a story-progress-only preset, going forwards and
      backwards. Add the result to "Tested in the game" in the README.
- [ ] **(in game)** Downgrades in story-progress mode: go from a late preset back to an early one
      and check that the dungeon that was reset is playable from its start.
- [ ] **(in game)** The deaths counter. The reader shows 0 on a full playthrough with no deaths,
      but the decomp's labels for that field look off. Die once, save, and check it reads 1.
- [ ] macOS and Linux: card and states locations come from BlueWake's source and are untested.
      Ask someone on those systems to try *Open card…* and *Write to card*.
- [ ] Python versions: tested on 3.14 on Windows. Check the minimum (3.10) actually works.

## Research

- [ ] **Which story flags are required.** Story-progress mode currently guesses from the flag
      descriptions. Two sources to build a real list from:
  - the Wind Waker Randomizer's logic files, which list what each check requires;
  - its new-file patch, which sets about 50 story flags so the game can be played out of order.
  Compare both against the catalog's story-flag timeline.
- [ ] **Chart numbering.** The save stores owned, opened and salvaged charts as numbered bits,
      but the game gives charts through one function that reads the number from the chest or NPC.
      Find each chart's number by comparing catalog saves from before and after getting it, then
      add a Charts section.
- [ ] **Event registers** (the counters stored among the story flags, like `0x7EFF` and `0xA60F`).
      `0xA107`, `0xA207` and `0xA307` look like per-dungeon progress (Forbidden Woods, Dragon Roost
      Cavern, Earth Temple), possibly map, compass and boss key. Confirm by comparing saves from
      just before and after picking up a dungeon map.
- [ ] **Sea room 0.** Disc stage `sea` has 50 rooms for 49 squares. Room 0 spawn 0 loads near
      Windfall; what it is for is unknown.
- [ ] **Big Octo and the Great Fairy.** Big Octo's defeat is a switch in its sea square's area
      progress (`d_a_daiocta.cpp`). The Great Fairy (`d_a_bigelf.cpp`) is not fully decompiled;
      find what she checks before giving double magic.
- [ ] **Items given by NPCs versus inventory.** With a Grappling Hook given early, does Medli
      still hand it over in Dragon Roost Cavern? Tells us whether that scene checks a flag or the
      inventory.

## Features

- [ ] **Read and write cards directly**, in Python, instead of through BlueWake's
      `card_to_gci.py` and the compiled injector. BlueWake's `scripts/card_container.py` documents
      the container format (GPLv3, same as this project). Removes the build step from setup.
- [ ] **Charts tab**, once the numbering is known (see Research).
- [ ] **Event register editing**, once their meanings are known.
- [ ] **Pictographs**, including the Legendary Pictograph. They are photos, stored apart from the
      quest log; work out where and how before offering them.
- [ ] **More named restart spots.** Add confirmed spots (like Windfall's post-rescue alcove,
      `sea 11 128`) as they are found, and list a room's spawn points by name where known.
- [ ] **Better story presets.** The current ones are tests made from save states taken whenever
      it was convenient during play. Replace them with states made at deliberately chosen points
      in the story, or with presets built from the required flags, items and spawn points once
      the Research items above are settled.
- [ ] Clean preset files: `make_presets.py` copies whole saves, so the two unused quest logs in
      each preset hold whatever was on the card. Blank them when copying.

## Polish

- [ ] Window layout on smaller screens (it needs about 1050 × 900).
- [ ] Remember the last opened card and quest log, not just the card written to.
- [ ] Warn when the card being written is newer than when it was opened (BlueWake saved to it in
      the meantime).
- [ ] Story flags: let the area grouping be corrected by hand, and save the corrections.
- [ ] A packaged download (for example a single `.exe` built with PyInstaller) for people without
      Python.
- [ ] Screenshots in the README.

## BlueWake

- [ ] **Mod-menu version.** The BlueWake developer was interested in an editor in the F1 menu.
      Write a short spec for them: every offset and rule the editor uses, where each comes from in
      the decomp, and which ones are confirmed in game. An in-app editor could also edit the live
      save in memory (`0x803C4C08`) instead of the card.
- [ ] Keep the decomp and Randomizer sources current: re-check offsets if BlueWake's verified
      source changes (its digest has been `54f54434…` since 0.5.0).
