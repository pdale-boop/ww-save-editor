# King of Red Lions / Dragon Roost arc, part C: the cavern to Din's Pearl

Draft for `research/arcs/` (`korl_c.json`), written 2026-10-09. Covers Dragon Roost Cavern through Din's Pearl
and the King of Red Lions' next hints, up to sailing for Forest Haven. Parts A and B cover everything before the
cavern; the next arc starts at the Forest Haven arrival (0x0A20). Decomp references are zeldaret/tww (CC0);
nothing here is tested in game.

## The cavern is three stages

All three save to area 3 (`STAGE_DRC`), and saving in any of them restarts at `M_NewD2` room 0 point 0, their
exit 0 (`dComIfGs_setGameStartStage`; `wwedit.disc_restart_places`; catalog 09 and 10 have that restart).

- `M_NewD2`: the dungeon. Room 9's archive is an empty placeholder (105 bytes).
- `M_Dra09`: room 9 as a stage of its own, where Medli is held: Medli (`Md1`), two Bokoblins (`Bk`), the
  shutter doors (`Mori1`, `fpcNm_MDOOR_e`), an all-enemies switch (`AND_SW0`), an event switch (`Evsw`),
  a switch area (`SW_C00`), Valoo (`dragon`) and the rain cloud (`Rcloud`). Its exits lead to `M_NewD2`
  room 10 and room 7. `daNpc_Md_c::isTypeM_Dra09` is her type for this stage.
- `M_DragB`: Gohma's room: Gohma (`Btd`), Valoo's tail (`Dr2`), the warp (`Warpf`).

Dungeon items are area 3's `dSv_memBit_c::mDungeonItem` (offset 0x21 of the area block; bits `MAP`,
`COMPASS`, `BOSS_KEY`, `STAGE_BOSS_ENEMY`, `STAGE_LIFE`, `STAGE_BOSS_DEMO`, `d_save.h`). The catalog has 0x00
at 08, 0x03 at 09 and 10, 0x3F at 11.

## Steps

| Step | Sets | Evidence |
|---|---|---|
| `cavern_lava` | 0x0380; map, compass | 0x0380 is loaded twice in `daObjMagmarock::Act_c::demo_move`, the lava slab's camera scene (compiled `d_a_obj_magmarock.rel`, `.text` 0x150 and 0x228, inside the function at 0x128-0x258 per `config/GZLE01/rels/d_a_obj_magmarock/symbols.txt`; the decomp has no setter). `d_a_bwdg.rel` loads it too (not read). |
| `medli_rescued` | 0x1140, 0x1101; Grappling Hook; switch 0x32; optional 0x1280 | 0x1140: the type-1 shutter opens after the fight (`daMdoor_actionReady`, `d_a_mdoor.cpp:330-345`). 0x1101: Medli's talk (0x17DD on) gives the hook and sets it at message 0x17E4 (`d_a_npc_md.cpp:5117-5119`, `5353-5357`). Switch 0x32 follows 0x1101 through `Evsw` 0x03110132 (`d_a_tag_evsw.cpp:14-15, 36-37`). 0x1280: her next talk 0x17E5 or a player state she sees (`:5121-5123`, `:1578-1583`). |
| `cavern_hook` | 0x0580; switch 0x2E; boss key; optional 0x2A10 | 0x0580: the hook catching a placed grapple point (`Kui` parameters without bits in 0xF0; all 84 on the disc), `d_a_himo2.cpp:1143-1148`. Switch 0x2E: Medli's (`Md1` 0x002E0200, `m3100`, `d_a_npc_md.cpp:5627`); with 0x1101 she flies off (`:1607-1608`); `SW_C00` 0x0003FF2E sets it (`d_a_swc00.cpp:21`). 0x2A10: the flame lift in room 2 when its last rope is cut (`d_a_mflft.cpp:200-203`), not needed to reach room 9. |
| `gohma` | 0x0420, 0x0540, 0x3D80; boss scene, boss beaten, heart container | Boss scene `d_a_btd.cpp:431`; 0x0420 first pull on the tail (`d_a_himo2.cpp:1351-1354`); 0x0540 the hook catching the tail, whose grapple point Dr2 creates with 0x511 (`d_a_dr2.cpp:812-816`, `d_a_himo2.cpp:1144-1146`); boss beaten `d_a_btd.cpp:2190`; 0x3D80 `dMeter_recollect_boss_data` (`d_meter.cpp:1070-1074`); heart container `item_func_utuwa_heart` (`d_item.cpp:588-602`). |
| `valoo_pearl` | 0x3908; Din's Pearl | `WARP_WIND` → `Adanmae` 100 (layer 8) → `demo41` (`howling.stb`) → `sea` 13 point 210 (layer 9) → `getperl_komori` (`getperl_komori.stb`, item payload 3 = Din's Pearl via `d_a_demo00.cpp:714-735`) → `sea` 13 point 212. 0x3908 is the clouds lifting (`daObjRcloud_c::clouds_lift_act_proc`, `d_a_obj_rcloud.cpp:166-173`). |
| `korl_din_talk` | 0x0A80 | Forced message 0x5EC with the pearl (`daShip_c::checkForceMessage`, `d_a_ship.cpp:347-348`); 0x5ED sets 0x0A80 (`:635-636`). |
| `south_wind` | 0x1A80, 0x1980 | 0x1980 on boarding with 0x0A80 (`d_a_ship.cpp:1569-1574`), offered only with a south wind (`:4148-4160`). 0x1A80 when a room unloads while Link owns Din's Pearl (`d_s_room.cpp:125-127, 266-267`). No order between the two is forced. |

The cavern's warp pots are event register 0xA207, not a flag: `daObj_Warpt_c::m_event_reg[0]`, one bit per pot
(`d_a_obj_warpt.cpp:37-44, 284-289`; `Warpts1`-`3` in `M_NewD2` rooms 0, 2 and 10). The TODO's guess that 0xA207
is map/compass progress differs from my reading: it's the pots (0 -> 7 between catalog 08 and 09). By the same
table, 0xA107, 0xA007, 0x9F07, 0xA307 and 0xA407 are the other dungeons' pots (which dungeon each is, by the
pot's parameters bits 4-7, wasn't checked).

## Catalog

| Entry | Position |
|---|---|
| 07, 08 | before `cavern_lava` (08: part B's Medli bottle, 0x1102/0x1104, done) |
| 09 | `cavern_lava` |
| 10 | `medli_rescued` |
| 11 and later | `south_wind` (all steps) |
| 48, 50, 51 (crafted) | mixed: the Grappling Hook given without the flags |

## Not placed

- 0x0901: set whenever a fishman dives away (`daNpc_So_c::modeDisappearInit`, `d_a_npc_so.cpp:1206-1209`); a
  fishman in Dragon Roost's square has a first talk of its own while it's off (`:566-568`, `:587-588`). Part of
  the fishmen and sea chart chain.
- Area 3 switch 0x3A, on between catalog 09 and 10: no actor tied to it yet.
- First on between 10 and 11 but outside this arc: 0x0A20, 0x1801 (Forest Haven), 0x0B08, 0x0C40, 0x1E10,
  0x2304 (Windfall at night, Song of Passing).

## Open

- Whether the slab scene (0x0380) must come before room 9: the catalog's order, not checked in the code.
- Whether the way to the boss needs the flame lift (0x2A10).
- `arcs.py` doesn't check pearls or dungeon items yet; the draft keeps them in unchecked keys
  (`pearls`, `dungeon_items`).
