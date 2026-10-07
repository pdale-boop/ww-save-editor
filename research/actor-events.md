# Actors that start named events (unverified index)

A sweep of the decomp (zeldaret/tww, `src/d/actor`) for actors that start a named event from their
own code: string literals passed to `dComIfGp_evmng_getEventIdx`, `dComIfGp_evmng_startCheck`,
`fopAcM_orderOtherEvent` and similar, and event-name tables. Made 2026-10-07 by a search agent.
**Not yet checked line by line.** Each row is a lead for chain mapping in `story-flags.md`, not a
finding. "Flags near" means read or set close to the order call, not traced through every branch.

Already mapped in detail (see `story-flags.md`): `d_a_npc_ls1` and `d_a_dk` (prologue,
`zelda_fly`), `d_a_obj_barrier` and `d_a_obj_YLzou` (endgame), Ganon's Tower tags (`g2before`).

## Main-story and quest-chain events

| Actor | Event(s) | Trigger | Flags near the order call |
|---|---|---|---|
| tag_island:65-73, 233-386 | ARRIVAL_DRG2/GND2/WND2/TWN2/FST2/BRK2, PUROLO_RETURN2, TACT_TEARCH0-4 (also stage events by `getEventNo`) | island arrival | `getArrivalFlag` L78-88: 0902, 0A20, ENDLESS_NIGHT, 1F04, 2E04, 2E02, 3E10 (set as the event starts). Gates: 1608 (Earth), 1604 (Wind); bomb bag for type 7 |
| tag_event:368-399 | SUPERELF, fairy_flag_on_Jmp, fairy_Jmp, BEAST_GATE2, plus stage events by type | proximity/arrival | 1001, 1820, 2740 (set); per type: 0004, 0101, 0E20, 1101, ENDLESS_NIGHT, 3B20, 2502, 3040, 2110, 3202 (L80-150, 270-305) |
| obj_YLzou:37-40, 383, 507 | move_YLzou, go_up_stairs, go_up_stairs2 | on creation, gated by flags/switch | MASTER_SWORD_CUTSCENE, MASTER_SWORD_SWINGING_CUTSCENE, HYRULE_COURTYARD_CUTSCENE, MOVED_HYRULE_STATUE, ZELDA_AWAKENED, triforce count, 2C01, 3980 (L99-145) |
| warpdm20:123 | TO_HYRULE_WARP | warp | 2D08; sets 1820 if ZELDA_AWAKENED (L118-126) |
| warphr:133-135, 171 | TO_SEA_WARP_1/_2, warp_out | warp | 2D08; 3810 (L207); 1001 (L399) |
| warpgn:130-131 | TO_MAJYUU_WARP, APPEAR_WARP | switch | 3D02 (L190, L407) |
| warpf:273-275 | WARP_WIND, WARP_WIND_AFTER | warp | pearls / 2D10 (L225-231) |
| obj_doguu:255-258 | DOGUU_DEMO1-3, MEGAMI_DEMO | item (pearl placed) | PLACED_DINS/FARORES/NAYRUS_PEARL (L497-517); 1E40 (L738) |
| obj_vgnfd:44-47, 316 | 4_door_dn/mr/dc/kz, 4_door_fin | on creation | TRIALS_DOOR_LIGHT_*, *_TRIALS_CLEAR (L30-41); 3204 (L278) |
| obj_rcloud:12 / kytag05:51 | demo41 | reacts to a stage event | rcloud: 3908 (L94, set L172) |
| kytag06:27 | ARRIVAL_BRK | reacts only | none |
| obj_ajav:153-157 | ajav_destroy0/1, ajav_uzu (Jabun's cave stone) | item (bombs) | none in file |
| obj_hsehi1:258, 418 | hsehi1_tact, hsehi1_talk | Wind Waker song / talk | 2510 (L221); 2B10 (L277, set L652) |
| npc_bm1:503-508, 1188 | Get_Mo3_Ltr, Met_Ryu_Islnd, Get_Rupee, Skn_Islnd | on creation or talk | 1A80, 1820, 2E04, 1401, 2202, 2120, 2001, 2140, 2180 (L1498-1676, 3157-3166) |
| npc_cb1:2909, 2651 | cb_rescue, cb_tact, cb_tactCancel, cb_sow | arrival / song | 1610, 1604 (L1595-1596); 1880, 1840, 1904 (L2701-2740) |
| npc_md:214, 5021 | Md_ItemGet, Md_RopeGet, MD_FLY, md_cliff, Md_Fly2, Md_Tact, Md_TactTrue, Md_HarpTalk | on creation, song, talk | 2E40, 3B80, 2C08, 1620, 1101, 1140, 1280 (set L1582), 1402, MEDLI_GAVE_FATHERS_LETTER, 4001, 4180 |
| npc_os:2019, 1901 | Os/Os1/Os2 _Wakeup, _Finish, _Message, _Finit0/1 | song / arrival | 1780, 1740, 1720, 1710, 1704, 1B01 (L389-450); 2510, 2608, 2604 |
| obj_vmc:172 | cb_sow (Forest Haven sprout) | item / song | 3420 (L286) |
| obj_vfan:80 | Vfan | switch | 3A08 (L192) |
| obj_homen:329 | homen_down | not checked | 3410 (L565), 3880 (L745) |
| tag_md_cb:18, 472 | md_/cb_tag_message (+_carry, _fm), cb_tag_message_sekizo | proximity | 33xx and 34xx series, 4001, 4180 |
| npc_tc:638, 655 | TC_JUMP_DEMO, TC_RESCUE, TC_TALK_NEAR_JAIL*, TC_GET/PAY_RUPEE | talk / proximity | 0B40, 0B80 (set L1464), 1708, 1A20 |
| npc_so:1436-1462 | SO_1ST_MEET(_END), SO_MAPOPEN, SO_BOW, SO_GET_RUPEE, SO_TRIFORCE_CHECK | talk / on creation | 0901 (set L1208), 3A10 (L1165), 3A20 (L1328), 1E40 |
| npc_hr:256-1592 | TACT_HT, TACTM_RT, TACT1_RT, PATTEN_RT, INTRO_RT(_F), TACT0_RT, HT_TALK | song / arrival | 3D01 (L1532, set L1560); 2708 (L485); 2710 (L681) |
| npc_tt:29-315 | TACT_TT10-13 (Ballad of Gales) | song | 0B08, 0C40 |
| tag_mk:136-140, 287 | tagwp, tagwp2, tagwp3, MK_PENDANT | proximity / roll into tree | 1E02 (set L273), 1E04, 2D80, 3380, 2D08, ZELDA_AWAKENED |
| npc_mk:1051-1214 | MK_GAMESTART, MK_GAMESET, MK_TALK–MK_TALK4, MK_DROP | talk | 1340, 1380, 1210, 2201, 1E02, 1E04, 1208, 1602, 1F80 |
| npc_ji1:4760-4777 | Ji1_* (training, spin attack, sword; 18 events) | talk | 0501, 0520, 0640, 0F10, 0F20, 0D80, 0108, 0002 |
| npc_p1:593 | sea_exp_cam | talk | 0820 (set L529), 0808, 0910, 0880, 0840 |
| npc_ho:632 | HO_PREACH | talk | 1F80, 1C04, 1C08, 1E01, 1380 |
| npc_btsw:281 / npc_bmsw:895 / npc_rsh1:467 / npc_bs1:1566-1612 | GETMOTHERLETTER; SHIWAKEGAME(2); RSH_GET_DEMO; BS1/BS2_GETDEMO, tickets | talk / item | btsw 2701-2704, 3104; bmsw 1A01-1A02; rsh1 1108, 1110, 0E08, 2420; bs1 1F08-1F20, 2008-2040, 3B04 |
| tag_volcano:153 / obj_volcano:189 / obj_iceisland:78 | TAG_VOLCANO, FREEZE/FIRE_VOLCANO, MELT/FREEZE_ICE | proximity / item | 1901, 1902 (tag_volcano L134-136) |
| oship:738 / tag_ghostship:64 | GOLD_SHIP_DELETE / PSHIP_CLEAR | not checked | oship 3E80 (L732) |
| mdoor:133 / lbridge:86 / obj_hbrf1:43 / obj_bemos:1340 | MORI1_EVENT / EFFAPPEAR, BRIDGE_DISAPPEAR / LiftMove / hmos3cam | switch | mdoor 1101, 1140; lbridge 0E01, 0F40; hbrf1 1508-1540; bemos 1010 |
| obj_mknjd:60 / npc_mn:442 / npc_mt:491 | MKNJD_D/K _DEMO, _CHECK, _ERROR, _LESSON / FIGURE_HATCH_OPEN / MT_GET_ITEM | song / talk | mknjd 0430 (L774); mn 2F04-2F08, 3120, 3D08; mt 3D08, 2F01, 3F01, 4040, 4080 |
| not checked | eskban Eskban; msdan2 Msdan2; hha hha_close; mkiek MkieK_die; hami3/4 AMI3/AMI4_OPEN; lstair STAIRAPPEAR; pfall NZFALL; warpls TOWER_WARP_U/D, DUNGEON_WARP; wbird TACT_WINDOW(2); daiocta DAIOCTA_*; tag_ba1 Use_Fairy | — | none found in those files |

## Generic and minigame events

auction AUCTION_*; cc CyuCyu; canon Canon_game; goal_flag race_*; apzl and d_meter PUZZLE_*;
npc_people UO1/UB1/UB4/UW2/UM1/UM3/SA3/SA5/UG1 talk and get-item events (flags not checked);
npc_photo PHOTO_*; npc_roten ROTEN_*; tag_photo, tag_hint; kamome kamome_call; ship
SV_TALK_P1/P4; salvage SALVAGE_*; tbox DEFAULT_TREASURE*; agb, agbsw0;
DEFAULT_TALK/GETITEM/SWITCH/PITFALL/WARP; shutters and doors; fire, ep SHOKUDAI; rd, fm, nz, dai,
kmon; obj_figure FIGURE_CHECK; obj_ferris kanran_*; OPTION_CHAR_END (md, os, kamome, cb1).

## Gaps

tag_island, tag_event and the andsw0/andsw2/ladder/swpush/stone2/tag_etc actors take their event
name from the stage's event list by number (`getEventNo`). Those names live in the stage data on
the disc, not in code.
