# Spawn points with no named way in

Research note, 2026-10-09. Starting point: 452 of the disc's 1,159 spawn points had no exit, cutscene,
code path, fall or save rule leading to them (`wwedit.disc_exits` / `exits_to`, as of the working copy after
6e8456d, with the built-in events, Ghost Ship, statue and save-continue entries). Sources: the zeldaret/tww
decomp and the USA disc. Guesses are marked as guesses.

Result: 224 more are explained. 228 remain, 82 of them in unused or test stages.

| Explanation (first that applies) | Points |
|---|---|
| Named before this note | 707 |
| New code paths (Deku Leaf tags, Outset's whirlpool, Floormaster/hole) | 5 |
| Collision restart numbers: falls, and saves on islands (section 2) | 43 |
| Developers' stage select only (`Menu1.dat`, section 1) | 176 |
| Unexplained | 228 |

The stage select lists 220 of the 452; 44 of those are also reached in play by the first two rows.

## 1. The one-point-per-room points: the developers' stage select

`d_s_menu.cpp` is a scene that lists stages and rooms and changes scene to the chosen one:
`dScnMenu_Execute` calls `dComIfGp_setNextStage(room->stageName, startCode, room->roomNo, room->layerNo)`.
Its list is loaded from `/res/Menu/Menu1.dat` (`phase_1`), which **is on the retail disc** (22,208 bytes).

Layout (`include/d/d_s_menu.h`, relocated in `phase_2`; all offsets from the file start, big-endian):

- `menu_inf` at 0: `u8 num` (groups), then at 4 the offset of the group table.
- `stage_inf`, 0x28 bytes: name (0x20, Shift-JIS), `roomNum` at 0x21, offset of its rooms at 0x24.
- `room_inf`, 0x2C bytes: name (0x20, Shift-JIS), stage name (8) at 0x21, `roomNo` (s8) at 0x29,
  `startCode` at 0x2A, `layerNo` (s8) at 0x2B. R/L in the menu can override the start code.

The disc's file has 40 groups and 468 entries. Matching an entry to a point the way `dStage_playerInit`
does (a room's list by its room, a stage's own list by id alone), 220 of the 452 unnamed points are menu
entries, among them nearly every dungeon room's point (Tower of the Gods `R01` to `R23`, Forbidden Woods,
Earth and Wind Temples, Dragon Roost Cavern, Ganon's Tower), the Savage Labyrinth rooms, `KATA_RM`'s
test rooms and most sea islands' point 0.

Nothing in the decomp changes to this scene: `fpcNm_MENU_SCENE_e` appears only in its own profile
(`g_profile_MENU_SCENE`) and the profile list. So in normal play these points are only reached by
developers. They are safe restart places as far as `dStage_playerInit` goes (the point exists), but the
game never writes them.

Useful side findings from the entry names (Shift-JIS, translations mine):

- Sea room 0: two entries in the group 大海原 ("Great Sea"), named 実験 ("experiment") and 沖合い
  ("offshore"). It is a test room for the open sea, not a sea floor.
- Windfall (`sea` 11) entries name its layers: 昼0 day 0 (layer 0), 夜0 night 0 (layer 1), 海賊 pirates
  (layer 3), 昼2 day 2 (layer 4), 夜2 night 2 (layer 5). Taura (タウラ島) is Windfall's Japanese name.
- `sea` 11 point 200 is the demo entry （８）タウラ島で船との出会い, "(8) meeting the boat on Taura
  Island", layer 8.
- The デモ ("demo") group has 48 entries: cutscenes with their stage, room, point and layer. Useful for
  the developer-saves item in TODO and `research/cutscene-triggers.md`.

Other users of room points, checked:

- `dStage_restartRoom` (start point -1) and the "turn restart" (-3) use a stored position, not a point id
  (`dStage_playerInit`, the -1 and -3 branches). They explain no points.
- Floormasters (`Fmaster`, `Fmastr1`, `Fmastr2`: `d_a_fm`) and holes (`Ypit00`, `Pitfall`:
  `d_a_obj_hole`): when the grab or fall ends they use their own exit from the room's list if the low byte
  of their parameters isn't 0xFF (`dLib_setNextStageBySclsNum`), else point 0 of the same stage in their
  room (`dComIfGp_setNextStage(dComIfGp_getStartStageName(), 0, current.roomNo)`). On the disc: 50
  Floormasters and 85 holes; only 2 rooms use point 0 (`KATA_RM` rooms 21 and 23, test rooms), the rest
  use exits already counted.
- The Deku Leaf: a return tag (`ReTag0`, `d_a_tag_ret`) touched by Link calls
  `daPy_lk_c::onDekuSpReturnFlg(linkID)` (parameters bits 0-7). A fall while that flag is on restarts at
  that point in room 41, Forest Haven (`dComIfGp_setNextStage(..., i_point, 41, ...)` in the player's fall
  handling). The disc has 10 tags, all in `sea` 41 (`SCOB`/`SCO7` chunks), for points 1, 2, 3, 4, 6, 7, 8.

## 2. The sea, and collision restart numbers

54 sea points were unnamed. Most are an island's point 0, and they are reached in play:

- **Collision restart numbers.** `daPy_lk_c::checkIsland()` (`d_a_player_main.h`) returns `mRestartPoint`,
  which the player sets from the ground it stands on (`dBgS::GetLinkNo`, the low byte of the polygon's
  `m_info1`; 0xFF is none). `dComIfGs_setGameStartStage` uses it for a save on the sea (once the island's
  landing event is done), and the player's fall handling uses it for a fall (same stage and room). Every
  room's `room.dzb` was scanned: 43 unnamed points are named by their room's collision (37 on the sea, 4 in
  `Obshop`, 1 each in `LinkUG` and `Ojhous`). Almost all sea islands' collision names only point 0; Mother
  and Child Isles (`sea` 9) names 0 and 1, which explains its boat point 1.
- `sea` 41 points 7 and 8 (Forest Haven, y 3068 and 4926): Deku Leaf return tags (above).
- `sea` 44 point 151 (Outset, boat): the whirlpool. `Auzu` (`d_a_obj_auzu`) on Outset's layers 5 and 7,
  parameters 0x971C, link id (bits 8-15) 151. It calls `daShip_c::onWhirlFlg(id, linkID)`; when the boat
  has sunk far enough `daShip_c` sets flag 0x1940 and changes scene to that point in its room
  (`dComIfGp_setNextStage(dComIfGp_getStartStageName(), m03B2, fopAcM_GetRoomNo(this))`).

The `sea` stage's own exits after the 196 fall entries (4 per square) are all boat arrivals at point 99
(start mode 9):

| Entries | Square (point 99) | Used by |
|---|---|---|
| 196 | 1 | `0xC5 + warp area` with warp area -1 (cancelled); guess: unused |
| 197 | 9 Mother and Child Isles | Ballad of Gales |
| 198-205 | 11 Windfall, 13 Dragon Roost, 23 Greatfish, 26 Tower of the Gods, 41 Forest Haven, 44 Outset, 17 Tingle Island, 39 Southern Fairy | Ballad of Gales, and Cyclos's cyclone at random |
| 206-211 | 1 | unknown; guess: padding |

Evidence: the Ballad warp is `dStage_changeScene(mTactWarpPosNum + 0xC5, ...)` in `d_a_ship.cpp`, with the
warp area number set from the sea chart's warp table (`d_menu_fmap.cpp`, `setTactWarpPosNum(warpAreaNo)`;
the table itself wasn't read). A cyclone grabbing the boat picks `cM_rndF(8) + 0xC6`, clamped to 0xCD
(`d_a_ship.cpp`, the tornado code), so entries 198-205. These points were already counted as named (from the
sea's own list) but `disc_exits` labels them as plain "The Great Sea"; see the proposals.

Still unexplained on the sea (8):

| Point | Where | Notes |
|---|---|---|
| 3/10, 15/10, 19/10, 28/10 | Northern, Western, Eastern, Thorned Fairy Islands, y 632, walking in | Next to point 1, the fountain entrance (exits from `Fairy01`-`Fairy05`). Guess: where the Great Fairy (`d_a_bigelf`, not fully decompiled) sends you out. |
| 11/16 | Windfall, same spot as point 0 | A duplicate of 0. |
| 11/20 | Windfall, y 1039 | |
| 38/99 | Shark Island, boat warp mode | Not one of the warp entries. |
| 44/6 | Outset lookout, y 1650 | See `research/cutscene-triggers.md` (lookout points 6, 201, 206). |

## 3. What is left, by stage

Update (2026-10-09): the stage select's names say what two of the unused stages are: `sea_E` is the
sea for the epilogue (24 of the unexplained points) and `Cave08` an early Wind Temple (its entry is
"Makar kidnap test"; 21 points). `KATA_RM`'s rooms are one per enemy.

228 points (the table below was made before the collision scan, which took only `sea` 9/1 out of it).
Stages described as "Unused" in the Randomizer's stage names: 82 points (`sea_E` 24, `Cave08` 21,
`I_SubAN` 17, `DmSpot0` 5, `Amos_T` 2, `SubD45` 2, and one each in `E3ROOP`, `Ebesso`, `ITest61`, `kazan`,
`morocam`, `Mukao`, `PShip2`, `PShip3`, `SubD51`, `TF_05`, `TF_07`). The rest, in stages the game uses:

| Stage | Points | Kinds | Notes |
|---|---|---|---|
| `M2tower` FF tower (2nd) | 21 | stand 19, walk 2 | room 0 points 0-20 |
| `Mjtower` FF tower (1st) | 20 | stand 19, walk 1 | room 0 |
| `ma3room` FF interior (3rd) | 17 | stand 12, event 3, walk 2 | |
| `Cave11` Savage Labyrinth | 13 | fall 12, jump 1 | rooms no exit reaches (0, 6, 16-20) |
| `TF_06` Dragon Roost secret cave | 12 | door 12 | rooms 2-5, points 2-5: a room's points for each other room's door |
| `GanonC` | 7 | stand 5, door 2 | |
| `ma2room` FF interior (2nd) | 6 | | |
| `majroom` FF interior (1st) | 4 | | |
| `MajyuE` FF exterior (1st) | 4 | stand | points 16, 19, 20, 21 |
| `Siren` Tower of the Gods | 4 | stand | rooms 12, 15, 20, 23 point 0 |
| `Ocean` | 3 | | points 1 (the pirates, `d_a_npc_p1`, pinned), 2, 10 |
| `Atorizk` Rito Aerie | 2 | | points 209, 210 |
| `Cave10` Savage Labyrinth | 2 | | room 0 (no exit reaches it) |
| `Hyrule` | 2 | | points 1, 235 |
| `Obshop`, `SubD71` | 2 each | | |
| one each | 19 | | `Adanmae` 3, `Asoko` 255, `A_mori` 1, `A_umikz` 1, `GanonB/D/E` 1, `kaze` 17, `kenroom` 1, `kindan` 16/1, `M_Dai` 20/23, `M_NewD2` 16/0, `Ojhous2` 0, `Orichh` 5, `Pdrgsh` 1, `Xboss2` 228, `Xboss3` 231 |

Guess for the Forsaken Fortress stages (72 points): restarts after being caught by a searchlight or a
Moblin (`d_a_mo2` already sends you to `majroom` 0 0), or points set by actors with a computed target that
weren't read. Not checked.

## Proposed changes to `wwedit.py` (for merging; not made here)

`CODE_EXITS` entries, keys `(stage, room, point)`:

```python
# The Deku Leaf: a return tag (ReTag0, d_a_tag_ret) sets daPy_lk_c's Deku Leaf restart point; a fall
# then restarts at that point in room 41 (Forest Haven). Tags on the disc: points 1-4, 6-8.
**{('sea', 41, _p): [('sea', 41, 'a fall with the Deku Leaf after passing a return tag (ReTag0)')]
   for _p in (1, 2, 3, 4, 6, 7, 8)},
# Outset's whirlpool (Auzu, d_a_obj_auzu, layers 5 and 7): the boat is pulled under and arrives at
# the whirlpool's link point (daShip_c, flag 0x1940).
('sea', 44, 151): [('sea', 44, 'the whirlpool (Auzu, layers 5 and 7) pulling the boat under')],
# Floormasters and holes without an exit of their own: point 0 of the same room (d_a_fm, d_a_obj_hole).
('KATA_RM', 21, 0): [('KATA_RM', 21, 'a Floormaster or a hole with no exit (point 0 of the room)')],
('KATA_RM', 23, 0): [('KATA_RM', 23, 'a Floormaster or a hole with no exit (point 0 of the room)')],
```

In `disc_exits`, label the `sea` stage's own entries after the fall entries:

```python
elif room == -1 and stage == 'sea' and i >= 196:
    src = ('*', -1, 'the Ballad of Gales warp' + (' or a cyclone' if 198 <= i <= 205 else '')
           if 197 <= i <= 205 else 'an entry of the sea exit list no code was found to use')
```

A collision source: for each room, read `room.dzb` (header `cBgD_t`: triangle count and offset at 0x08,
info count and offset at 0x28; triangles 10 bytes with the info index at +6; infos 16 bytes) and add
`(stage, room, n): [(stage, room, 'a fall or a save here (the ground names this point: dBgS::GetLinkNo)')]`
for each restart number `n` other than 0xFF.

A stage-select source, if wanted: read `res/Menu/Menu1.dat` with the layout above and label matching points
"the developers' stage select only: <group> / <name>" (the names are Shift-JIS Japanese). That would also
give the tab a name for most dungeon rooms (`R01`...).
