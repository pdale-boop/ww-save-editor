# Cutscene triggers for developer test saves

Working notes for the TODO item "Developer saves just before key cutscenes" (BlueWake section).
Four scenes, worked out 2026-10-07 to build audio test saves for BlueWake 0.6.0. Mostly from the
existing notes (`story-flags.md`, `arcs/prologue.json`, the catalog's flag timeline); new disc
reads are marked "disc", decomp reads "code". All four saves were then played in BlueWake 0.6.0
(they were used to confirm its cutscene audio fix): each loaded at its restart and its scenes
played. Results are under each section.

Method for each: find what starts the scene and what it needs (flags, items, stage switches),
start from the closest clean catalog entry, change as little as possible, and restart at a spawn
point that exists in the room's `PLYR` list (`wwedit.spawn_points`) and is close to the trigger.

## 1. Helmaroc King carrying Tetra (`zelda_fly`, Outset)

Already mapped in `story-flags.md` ("Prologue (Outset)") and `arcs/prologue.json`:
`omedeto` is a walk-up to Aryll (200 units), needs 0x2A80 on (her type 0), 0x0001 off and no
Telescope; `get_telescope` follows; the postman step needs the Telescope and sets 0x0310;
`zelda_fly` follows and sets 0x0001 (code).

New (disc, `sea` room 44 actors and `PLYR`):

- Aryll type 0 (`Ls1` params 0) is on layer 0 only (`ACT0`), on the lookout at
  (-195506, 1650, 313774). So the save must be in the day (06:00-18:00) and before 0x0101
  (Outset layer 9 after that).
- Lookout spawn points: 6 (y 1650), 201 (y 1700) and 206 (y 1650, start event `awake`, spawn
  switch 0x5C). 201 has no start event. Catalog 02 already has sea switch 0x5C on (area 0, +0x0C
  bit 0x10), which matches the `awake` spawn switch and supports the spawn-switch reading.
- 0x2A80's scene, `TALE_DEMO`, has spawn switch 0x02 in `LinkRM`; save area 11 holds it (switch
  byte +0x07 is 0x8F in every main-playthrough save from 44 on).

Save: catalog 02 + 0x2A80 + area 11 switch 0x02, restart `sea` 44 201.

Tested in BlueWake 0.6.0: loads on the lookout; the scenes play through to `zelda_fly`.

## 2. First Forsaken Fortress arrival (`ooi`, `majyuu_shinnyuu`)

Already mapped in `story-flags.md` ("First Forsaken Fortress visit"): with 0x0808 on and 0x0520
off, the game restarts at `MajyuE` spawn 18 (`dComIfGs_setGameStartStage`), the pirate ship
creates Tetra there, `ooi` is a walk-up (needs 0x0801 and 0x0804 off), `majyuu_shinnyuu` a
walk-up after 0x0804 (code).

New:

- `majyuu_shinnyuu` plays `maju_shinnyu.stb` (disc, `MajyuE` event list).
- `MajyuE` room 0 has only base actor lists, no layers (disc), so time of day doesn't pick its
  actors.
- Steps between catalog 45 and 03, from the timeline and an area-memory diff (45 -> 03): before
  0x0808 the playthrough set 0x0802, 0x3202, 0x1401, 0x2401, 0x0820, 0x0720, 0x0710; area 11
  switches 0x11 and 0x15 (Grandma's house: 0x11 is `LOOK_SHIELD`'s switch, 0x15 unknown); sea
  switch 0x2C (= `departure_DEMO`'s spawn switch, 44); area 13 chest 4 opened (the hold's Spoils
  Bag chest, inferred) and a visited-room bit; sea switch 0x0A (= `MEETSHISHIOH`'s spawn switch,
  so after the fortress). `mCollect[3]` (Pirate's Charm, by the decomp's collect layout) also
  turns on between 45 and 03; where it is given isn't settled. 0x0810 (Tetra sends Link to Niko)
  never turned on in the playthrough.

Save: catalog 45 + shield + Spoils Bag + the flags and switches above, restart `MajyuE` 0 18.
The Pirate's Charm collect bit was left off.

Tested in BlueWake 0.6.0: loads on the ship's deck; climbing the ladder to Tetra starts the
catapult launch (`majyuu_shinnyuu`).

## 3. Valoo after Gohma (`howling.stb`, then `getperl_komori.stb`)

Disc (`M_DragB` and `Adanmae` event lists, `PLYR`):

- `M_DragB` `WARP_WIND` (the boss warp) goes to `Adanmae` room 0, start code 100, **layer 8**.
- `Adanmae` spawn 100 has start event 1, `demo41`, which plays `howling.stb` and then goes to
  `sea` room 13 spawn 210, layer 9; spawn 210's event is `getperl_komori` (as in story-flags.md).
  `demo41`'s spawn switch is 255 (none).
- `M_DragB` `WARP_WIND_AFTER` goes to `sea` 13 spawn 211 (`BOSS_WARPOUT`).
- `Adanmae` layers 0 and 1 hold the `dragon` actor (Valoo); layer 8 has no actors in the room
  file. So a save restarting at spawn 100 would load layer 0/1 with Valoo placed, unlike the real
  entry: not tried.
- Gohma's room `M_DragB` room 0 has spawn 0 (mode 6) and 1 (mode 0), Gohma (`Btd`), Valoo's tail
  (`Dr2`) and the warp (`Warpf`) in its base list.
- Timeline 10 -> 11: Gohma's defeat is 0x3D80; 0x3908 is the Din's Pearl scene; area 3's dungeon
  bits go 0x03 -> 0x3F.

Save: catalog 10, restart `M_DragB` 0 1, health filled; the fight then leads into both scenes.
The game never saves a restart inside a boss room.

Tested in BlueWake 0.6.0 (during BlueWake bug-fix testing): the save loads as if Gohma's intro had
just finished, with Link on safe ground in the arena and Gohma not yet spawned. A few steps
forward start Gohma's cutscene. After the fight, Valoo's roar (`howling.stb`) and the Din's Pearl
scene (`getperl_komori`) follow.

## 4. Tower of the Gods rising (third pearl)

Timeline 18 -> 19: 0x1480 (Din's Pearl placed), 0x1E40 (tower raised), 0x2E80 (tower cutscene,
`towerd`/`towerf`/`towern.stb`, `ADMumi`), 0x3840 (King's text after). So Din's statue is the
remaining one in entry 18, and Northern Triangle Island is `sea` room 18 (entry 19 placed it after
sailing there).

Disc (`sea` room 18): `Doguu` (params 0x00FF00) is in the base actor list, so on every layer, at
(-160, 540, -100483). Spawn 0 is on the island at (-283, 300, -99600); 100-103 are ship spawns.
`d_a_obj_doguu` (per `actor-events.md`, not reread) checks the `PLACED_*` flags and sets 0x1E40.

Save: catalog 18, restart `sea` 18 0.

Tested in BlueWake 0.6.0: loads on the island; placing the pearl raises the tower.

## Open

- Where the Pirate's Charm is given (test 2 left its collect bit off and the scenes still played,
  so the arrival doesn't need it). From play, not yet checked in the decomp: Tetra slips it to
  Link offscreen around the launch, and it is revealed when she first calls him on it inside the
  fortress. The code that sets `mCollect[3]` would settle it.
- Whether `howling.stb` is what players call "Valoo's speech", or that is part of
  `getperl_komori`.
