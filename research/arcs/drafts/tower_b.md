# Tower of the Gods arc, part B: the Tower of the Gods dungeon

From entering the tower (after part A raises it, 0x1E40) to the warp down to Hyrule (part C starts at the
Hyrule arrival). Stages `Siren` (the dungeon, rooms 0-23), `SirenMB` (the Darknut miniboss, room 23),
`SirenB` (Gohdan), and `ADMumi` (the top of the tower). Sources: the zeldaret/tww decomp, the disc (US), the
Wind Waker Randomizer's logic (MIT), the developers' stage select, and the owner's rule that each dungeon's
new item is needed to reach its boss key. The catalog has no save inside the tower: 19 is before it, 20
after Hyrule, so the order inside comes from the code and the Randomizer's logic.

## Saving and areas

`Siren`, `SirenMB` and `SirenB` save to table 5 (`STAG`, `wwedit.stage_kind`), so their switches and dungeon
items are area 5. They are dungeon-type stages, so a save anywhere in them restarts at their exit 0,
`Siren` room 0 point 0 (`dComIfGs_setGameStartStage`; `wwedit.disc_restart_places`). `ADMumi` saves to table
0 (the sea's area) and is also dungeon-type: its exit 0 is `ADMumi` point 100, the top of the tower.

## Steps

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `tower_enter` | area 5 switch 0x63 | Room 0's entrance point 0 (params 0x00FF2000) is a boat arrival (start mode 2) that starts event 0, `moro_scam`, the first time; its spawn switch is 0x63 (`Siren` `EVNT` entry 0, byte 0x13), turned on by `dEvent_exception_c::setStartDemo` (`d_event_manager.cpp:41-48`) |
| window | `light_bridge` | 0x0E01, 0x0F40 | `daLbridge` (`d_a_lbridge.cpp`): the end of `EFFAPPEAR` sets 0x0E01, the end of `BRIDGE_DISAPPEAR` 0x0F40 (:204, :209); each plays only while its flag is off (:212-217) |
| window | `tower_map_compass` | area 5 MAP, COMPASS | `Siren` `TRES` chest 1 (room 3, behind bombable walls): item 0x4C, Dungeon Map; chest 2 (room 1, the skulls room): 0x4D, Compass. A stage-level chest's room is `home.angle.x & 0x3F` (`daTbox_c::searchRoomNo`, `d_a_tbox.cpp:276-279`); its item is `home.angle.z`'s high byte |
| 2 | `first_servant` | 0x1780, 0x2602, 0x1710 | `daNpc_Os_c` (`d_a_npc_os.cpp`, the Servants of the Tower `Os`, `Os1`, `Os2` in `Siren`'s stage actor list, arguments 0-2). Argument 0: `setWakeup` 0x1780 (:408-410), `setFinish` 0x1710 (:442-444, at the placing event's end :1333). 0x2602: the first time a Tower door of kind 1 lights up (`dDoor_hkyo_c::onFirst`, `d_door.cpp:835-838`) |
| 3 | `command_melody` | 0x2B10, 0x2510, Command Melody | The first statue in room 7 with its switch on and 0x2510 off orders event 7 (`eventOrderCheck`, :549). The stone tablet (`Hsh`, `daObj_hsh_c`, room 7) appearing sets 0x2B10 (`initialAppearEvent`, `d_a_obj_hsehi1.cpp:650-652`). Message 0xEF4 sets 0x2510 (`d_a_npc_os.cpp:1929-1932`) |
| 4 | `tower_bow` | Hero's Bow | `SirenMB` room 23 holds the Darknut (`Tn`); `Siren` `TRES` chest 3 (`takara8`, room 23) holds 0x27, the Hero's Bow. The miniboss entrance needs the Command Melody or the Bow (Randomizer `logic/macros.txt`) |
| 5 | `second_servant` | 0x1740, 0x1704, 0x2608 | Argument 1: `setWakeup` 0x1740 (:413), `setFinish` 0x1704 (:447); room 7 with its switch and 0x2608 off orders event 8 (:554), whose end sets 0x2608 (:1336). The kind-3 door blinks once the Command Melody is known until 0x1704 (`d_door.cpp:796-800`). Randomizer: the west servant needs the Command Melody and the Hero's Bow |
| 6 | `third_servant` | 0x1010, 0x1720, 0x1B01, 0x2604 | 0x1010: a wall Beamos (`Hmos3`, type 2; two in room 17) whose switch turns on sets it the first time and plays `hmos3cam` (`daBemos_c::event_move`, `d_a_obj_bemos.cpp:1329-1336`). Argument 2: `setWakeup` 0x1720 (:416), `setFinish` 0x1B01 (:450); event 9 (:559) ends with 0x2604 (:1339), the portal to the last floor. The kind-2 door blinks from 0x1704 until 0x1B01 (`d_door.cpp:802-806`) |
| 7 | `tower_boss_key` | area 5 BOSS_KEY | `TRES` chest 11 (`takara4`, room 17): 0x4E, Big Key; the Randomizer's "Big Key Chest" needs the third floor (all three servants) |
| 8 | `gohdan_intro` | area 5 STAGE_BOSS_DEMO | `daBst` (`d_a_bst.cpp`): `onStageBossDemo` (:2298); the intro is skipped once it's on (:1778) |
| 9 | `gohdan` | area 5 STAGE_BOSS_ENEMY | `d_a_bst.cpp:2432`, then a warp flower (:2436). Needs the Bow (or Hookshot) and Bombs (Randomizer). No recollection snapshot for Gohdan (`dMeter_recollect_boss_data` covers the other four bosses, `d_meter.cpp:1070-1086`) |
| window | `gohdan_heart` | area 5 STAGE_LIFE | `item_func_utuwa_heart` (`d_item.cpp:588-601`); max hearts 5.5 -> 6.5 in the catalog |
| 10 | `ring_bell` | area 0 switches 0x37, 0x39 | The warp flower plays `WARP_WIND` while 0x2D10 is off (`daWarpf`, `d_a_warpf.cpp:230-233`); `SirenB`'s `WARP_WIND` ends at `ADMumi` point 200, the top (falling in). The bell is rung with the Grappling Hook: `Kui` (`d_a_kui.cpp`, hookable posts) at y 31899, parameters 0x37FF0403, switch = parameters >> 24 (:485), set when swung on (:189, :305, :381). Three `TagEv` (0x013739FF: type 0xFF, waiting for switch 0x37, event 1) then start `JMP_DEMO` (`daTag_Event_c::arrivalTerms`, default case, `d_a_tag_event.cpp:51-70`), whose spawn switch is 0x39 (`ADMumi` `EVNT` entry 1). The developers' stage select calls `ADMumi` layer 9 "Tower, by the bell" |
| 11 | `warp_to_hyrule` | 0x2D10 | `JMP_DEMO` ends at `ADMumi` point 201, which starts `warp_in` (entry 0, no spawn switch); `warp_in.stb` sets 0x2D10 (decomp note) and the event ends at `Hyrule` point 200, where `warp_out` starts the first time. With 0x2D10 and no Master Sword the King's hint is "the power is in the castle" (`d_a_ship.cpp:362`, ladder rung 14); afterwards Gohdan's warp plays `WARP_WIND_AFTER` to `sea` 26 point 1 |

Every flag, switch and dungeon item above is off in catalog 19 and on in 20.

## Order

- Steps 2, 5 and 6 are fixed by the code: the doors light up for the next statue only after the previous one
  is placed (`d_door.cpp:790-806`), and the third statue's event opens the portal to the last floor.
- Step 3 follows step 2 (event 7 needs the first statue in room 7).
- Step 4 sits before the second statue and the boss key: the west servant needs the Bow (Randomizer logic) and
  each dungeon's new item is needed to reach its boss key (owner's play). Where the miniboss falls between
  steps 3 and 5 is Randomizer logic, not code.
- Map, compass, the light bridges' first scenes and the heart container have windows.

## Catalog (`arcs.position` on these steps)

| Entries | Position |
|---|---|
| 17, 18, 19 | not started |
| 20, 21 and later (41) | `warp_to_hyrule`, all windows done |
| crafted 50-56 | mixed (items given early) |

This holds once `arcs.owns` checks an item's "obtained" bit (`GOT_ITEMS`) instead of the slot's current item
id. With the current `owns`, every save from 23 on comes out mixed at `tower_bow`, because the Bow slot then
holds Fire and Ice Arrows or Light Arrows (`wwedit.BOW_ORDER`). The same would hit any upgraded item.

## Not placed

- Part C (Hyrule): 0x2D04, 0x3A04, 0x3802, 0x3810, 0x3B40 and the Master Sword.
- Event register 0xA60F (0 -> 1 between catalog 19 and 20): not identified.
- The tower's other area-5 switches (about 40 on in catalog 20) and small keys: puzzle state, not steps.
