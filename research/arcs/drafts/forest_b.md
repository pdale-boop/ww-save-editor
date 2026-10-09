# Forest Haven arc, part B: the Forbidden Woods

From entering the Forbidden Woods to beating Kalle Demos. Step list: `forest_b.json`. Part A ends on the
way in (catalog 14, on the platform before the updraft); part C starts where the boss's warp flower
leads, Forest Haven (`Omori` point 214).

## The stages

`kindan` (the dungeon), `kinMB` (miniboss) and `kinBOSS` (Kalle Demos) all have save table 4 in their
`STAG` chunk (`wwedit.stage_kind`: types 1, 6 and 3), so their switches, chests and dungeon items are
area 4. All three have exit 0 = `kindan` room 0 point 1, so saving anywhere in them restarts there
(`dComIfGs_setGameStartStage`; `wwedit.disc_restart_places`). Catalog 15 holds that restart.

Ways in and out (disc exits and event lists):

| From | To |
|---|---|
| `sea` 41 (Forest Haven's square) | `kindan` room 0 point 0 |
| `kindan` room 9 | `kinMB` room 10 point 0 |
| `kindan` room 16 | `kinBOSS` room 0 point 0 |
| `kinBOSS` event `WARP_WIND` / `WARP_WIND_AFTER` | `Omori` room 0 point 214 / 215 |
| `kindan` rooms 0, 5, 16 (warp pots) | `kindan` 0/1, 5/1, 16/2 |

## Steps

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `fw_entrance` | 0x2B20 | No decomp setter. One load in the compiled modules, `d_a_ss.rel` 0x14A8 (module archive; function not identified). `Ss` (`fpcNm_SS_e`) is placed 12 times in `kindan` (rooms 0, 1, 3, 4, 5, 9, 14): the door flowers. Catalog: off in 14, on in 15. |
| window | `fw_map_compass` | area 4 `MAP`, `COMPASS` | `item_func_map` / `item_func_compass` (`d_item.cpp:953-960`). Catalog: 0x00 in 14, 0x03 in 15. |
| window | `fw_boomerang` | Boomerang; area 4 switch 0x19 | `kinMB`'s chest holds item 0x2D (`daTbox_c::getItemNo`, `d_a_tbox.h:37`), chest 10 (`getTboxNo`, `:35`). The miniboss room's `Mori1` door opens on switch 0x19 (`daMdoor_c::getSwbit`, `d_a_mdoor.cpp:16-17`, `:149`). Catalog: off in 15, on in 16 (chest bit 10 too). |
| 2 | `fw_boss_key` | area 4 `BOSS_KEY` | `item_func_boss_key` (`d_item.cpp:963-965`); boss doors need it (`d_a_door10.cpp:360-364`, `d_a_door12.cpp:410`). |
| 3 | `kalle_intro` | area 4 `STAGE_BOSS_DEMO` | Played unless the bit is set, sets it (`d_a_bmd.cpp:2014-2018`, `:1416`). Creates Makar (`:1488`), who runs `rescueNpcAction` until the boss is beaten (`d_a_npc_cb1.cpp:2937-2938`; event `cb_rescue`). |
| 4 | `kalle_demos` | 0x3D40; area 4 `STAGE_BOSS_ENEMY` | `end()`: `onStageBossEnemy` and a warp flower (`d_a_bmd.cpp:561-563`). 0x3D40: `dMeter_recollect_boss_data` (`d_meter.cpp:1075-1077`), the rematch snapshot (`Xboss1`, `d_com_inf_game.cpp:1449`). |
| window | `kalle_heart` | area 4 `STAGE_LIFE` | Dropped by the boss (`d_a_bmd.cpp:747`); `item_func_utuwa_heart` sets the bit (`d_item.cpp:588-601`). |

Order: only the boss key before the boss is enforced by code (the boss door). Map, compass and the
Boomerang have windows with no end: the dungeon is built so the Boomerang is needed further in, but no
code read here requires it before the boss key or the boss, and Kalle Demos's own hitboxes exclude
boomerang hits (`d_a_bmd.cpp:1875`, `d_a_bmdfoot.cpp:758`). The heart container is optional.

## Warp pots: event register 0xA107

`daObj_Warpt_c::m_event_reg` (`d_a_obj_warpt.cpp:37-44`) lists one register per dungeon: 0xA207,
0xA107, 0xA007, 0x9F07, 0xA307, 0xA407. A pot picks its entry with parameters bits 4-7 (`:727`); the
Forbidden Woods pots (`Warpts1` room 0, `Warpts2` room 5, `Warpts3` room 16: parameters 0x..12, 0x..13,
0x..14) use entry 1, 0xA107, and set bits 0x01, 0x02, 0x04 by type (`:732-747`). Catalog: 0xA107 = 1 in
15 (the entrance pot), 7 in 16. `arcs.py` doesn't check event registers, so this is in notes only.

## Makar

Kalle Demos creates Makar during its intro and again, after the boss is beaten, until the player has
Farore's Pearl (`d_a_bmd.cpp:1488`, `1970-1976`). Makar's own code sets no saved flag in the boss room.
0x1904, set by Makar's message 0x14C4 (`daNpc_Cb1_c::next_msgStatus`, `d_a_npc_cb1.cpp:2708-2709`), is
his talk in Forest Haven after the ceremony (read locally from the message file), so it belongs to part
C; the catalog never has it on.

## Catalog

`arcs.position` on these steps: 13 and 14 not started; 15 at `fw_entrance` (map and compass done); 16,
17, 18 and 41 at `kalle_demos` with all windows done. Crafted 50 and 51 are mixed (Boomerang given early).

## Not placed

Area 4's other saved switches and chest bits (puzzle state), small keys (0 in 15 and 16), the Piece of
Heart that makes max hearts 5.5, and who sets switch 0x19 (the miniboss's death, not read).
