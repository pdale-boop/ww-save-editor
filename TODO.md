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
      `0xA207` is Dragon Roost Cavern's warp pots, one bit per pot (`daObj_Warpt_c::m_event_reg[0]`;
      `research/arcs/drafts/korl_c.md`), so `0xA107` and `0xA307` are probably the other dungeons'
      warp pots; maps, compasses and boss keys are per-area bits instead (`dSv_memBit_c`, area block
      + 0x21). Check the other two against `d_a_warpt`.
- [x] **Sea room 0.** A test room for the open sea: the developers' stage select
      (`/res/Menu/Menu1.dat`) lists it as "experiment" and "offshore" (`research/spawn-points.md`).
      Its one spawn point is a boat arrival near Windfall; nothing in normal play leads there.
- [ ] **Spawn points nobody reaches yet.** 755 of 1,159 are reached in play and 176 only from
      the developers' stage select; 228 are unexplained, 82 of them in unused stages and 72 in the
      Forsaken Fortress stages (guess: searchlight or Moblin captures). Details and the table in
      `research/spawn-points.md`.
- [ ] **Message text** (pinned 2026-10-09). A reader for the disc's message file would name
      conversations by their text, for example the pirates' messages 0xFA4/0xFA5 that decide
      whether they send Link to `Ocean`.
- [ ] **Big Octo and the Great Fairy.** Big Octo's defeat is a switch in its sea square's area
      progress (`d_a_daiocta.cpp`). The Great Fairy (`d_a_bigelf.cpp`) is not fully decompiled;
      find what she checks before giving double magic.
- [ ] **Items given by NPCs versus inventory.** With a Grappling Hook given early, does Medli
      still hand it over in Dragon Roost Cavern? Tells us whether that scene checks a flag or the
      inventory.

## Features

- [ ] **Progress sliders as the front page.** Not started until the chains are mapped
      (`research/story-flags.md`); the window is rebuilt around them, not before. Decided
      2026-10-07:
  - One slider per *story arc*, not per actor or flag group: an arc is what the player sees as
    one stretch of story, and its steps come from several actors. Example, the prologue: wake-up,
    Grandma and the clothes, birthday and Telescope, the postman, `zelda_fly`, the sword, the
    forest, Aryll kidnapped, setting sail with the pirates. Only fully mapped arcs get a slider;
    more as they are mapped. Moving an arc to step n puts steps 1 to n on, the rest off.
  - Chains converge and diverge (Makar needs the half-power Master Sword from Medli's chain; the
    main story contains both sage chains; the layers follow the main story), so moving one
    slider can move or limit others. Show the story order warnings as sliders move.
  - By default a step sets everything it involves: flags, items (pearls, sword level, the Cabana
    Deed), counters (the Joy Pendant total) and other records (the partner position).
  - A save whose chain isn't a clean "first n steps on" shows as mixed (for example "steps 3 and
    5 on, 4 off") instead of snapping to a position.
  - **Expert mode** toggle: each slider opens out into its individual flags.
  - Health as a stepped slider (heart containers and pieces) on the same page.
  - Design so it can become a controller-friendly tab in BlueWake's F1 menu (see BlueWake).
- [ ] **Read and write cards directly**, in Python, instead of through BlueWake's
      `card_to_gci.py` and the compiled injector. BlueWake's `scripts/card_container.py` documents
      the container format (GPLv3, same as this project). Removes the build step from setup.
- [ ] **Charts tab**, once the numbering is known (see Research).
- [ ] **Event register editing**, once their meanings are known.
- [ ] **Pictographs**, including the Legendary Pictograph. They are photos, stored apart from the
      quest log; work out where and how before offering them.
- [ ] **More named restart spots.** Add confirmed spots (like Windfall's alcove, `sea 11 128`,
      beside the King of Red Lions moored there) as they are found. The Restart place tab now
      says how Link arrives at each point and which exits lead there.
- [x] **Crafted restarts and the Tower night crash** (settled 2026-10-09). Not an editor bug: the
      crash in BlueWake's default build needs the Skull Hammer on Z, an in-game time before dawn,
      18+ hearts and a real clock from 19:00 together (tested in Tower room 0 with catalog 41's
      story), and every one of those is a value a player can have. Changing any one avoids it.
      The bug is BlueWake's (a jump into empty memory); the cards and notes are with its session
      (`CLOCK_CRASH_HANDOFF.md`). Nothing for the editor to change.
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
      save in memory (`0x803C4C08`) instead of the card. The progress sliders (Features) are
      the front page to carry over, as a controller-friendly F1 menu tab.
- [ ] **Developer saves just before key cutscenes**, so audio fixes (and other cutscene work) in
      BlueWake can be tested without replaying up to them. Each save has the scene's own flag
      off, everything before it on, and a restart place next to where it triggers. The flag
      chains in `research/story-flags.md` give the scene flags (for example the island arrival
      scenes, `daTag_Island`), and the story order check confirms the rest of the save is
      consistent. Scope: every scripted cutscene. The disc has 54 full cutscenes (`.stb`
      files, in `res/Object/DemoNN.arc` and a few stage archives); 24 story flags already
      have a decomp note naming the `.stb` that sets them. Shorter in-engine events (the
      stages' event lists) are many more and come after.
- [ ] **Quality-of-life skips, like Ship of Harkinian does for Ocarina of Time.** Two halves:
  - *In the save (this editor):* "already seen" story flags, stage switches and boss-intro bits
    skip cutscenes and camera pans, as the Randomizer's new file does (`init_save_with_tweaks`).
    Could be an option on presets once the flag chains are mapped (`research/story-flags.md`).
    Some first-time item fanfares are save data too: the Randomizer marks every spoil and bait
    as owned before (`0x803C4C9C`/`0x803C4C9D` in RAM) so their first pickup has no fanfare.
    Repeated nags may be save bits as well, like the King of Red Lions' "where to go next" hints
    (`daShip_c::setInitMessage`). The rule for all of these: only flip a bit where the code
    shows it can't soft- or hard-lock the game.
  - *In the game code (a BlueWake proposal):* item-get fanfares, chest-opening animations and
    the camera showing a puzzle switch's result run every time, so a save can't turn them off.
    New option sites alongside BlueWake's Better Wind Waker settings (`mods/betterww/options.txt`,
    `docs/MODS.md`) could skip them entirely, or end the cutscene early and give control back
    while the item's message box stays up until it times out. Find each site in the decomp
    first.
- [ ] Keep the decomp and Randomizer sources current: re-check offsets if BlueWake's verified
      source changes (its digest has been `54f54434…` since 0.5.0).
