# Jabun arc, part B: the Bombs to the King of Red Lions on Outset

From the Bombs on the pirate ship to the King's talk on Outset during the Endless Night, before Jabun's cave.
Step list: `jabun_b.json`. Part A covers the Endless Night and the pirate ship before the Bombs (Niko's rope game);
part C the stone slab, the whirlpool (0x1940), Jabun and Nayru's Pearl.

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `pirate_bombs` | Bombs, 0x0F02 | The hold's chest: `Asoko` `TRE2`/`TRE3` (layers 2\|3), tbox 5, item 0x31 (`d_a_tbox.h:35-37`). 0x0F02: `daNpc_P2_c::demo_bomb_get` (compiled `d_a_npc_p2.rel` .text+0x1CBC; Nonmatching in the decomp) |
| 2 | `korl_bombs_talk` | 0x1F02 | Forced message 0x624 with the Bombs (`d_a_ship.cpp:356-357`), which sets it (`:653-654`) |
| 3 | `outset_return` | 0x3E10, sea switch 0x74 | Outset's island tag, type 7: needs the Endless Night and the Bombs (`d_a_tag_island.cpp:112-127`); event `PUROLO_RETURN` |
| 4 | `outset_door` | 0x3E01 | Any scene-changing exit with 0x3E10 on (`d_a_player_main.cpp:10800-10804`) |
| 5 | `korl_outset_talk` | 0x3F80 | Forced message 0x1688 (`d_a_ship.cpp:365-366`, `:665-666`) |
| window, after 3 | `heal_grandma` | 0x2A20 | A Fairy in a bottle (`d_a_npc_ba1.cpp:121-125`); healing event (`:1324-1327`) |

## The Bombs

- The Bombs are the chest in the pirate ship's hold. `Asoko`'s `Stage.dzs` has the same chest in three layers:
  `TRE0` (layer 0) with item 0x24, and `TRE2`/`TRE3` (layers 2 and 3) with item 0x31, the Bombs
  (`item_func_bomb_bag`, `d_item.cpp:792-797`). `takara3` parameters 0xFF200280: tbox 5, no switch, shape 2,
  function 0 (`daTbox_c::getTboxNo`/`getSwNo`, `d_a_tbox.h:35-36`; item from angle z, `getItemNo`, `:37`). The ship
  is on layers 2|3 once 0x0520 is on (`getLayerNo`; `research/story-flags.md`). The Randomizer's location
  "Windfall Island - Pirate Ship" (original item Bombs, a minigame) lists the same two chests.
- Catalog 16 -> 17: the Bombs, and `Asoko`'s save area (13) gains chest bit 5.
- 0x0F02 has no setter in the decomp's source. The compiled modules load it only in `d_a_npc_p2.rel` ("NPC - Zuko,
  Niko, & Mako"): `demo_bomb_get` sets it (.text+0x1CBC, the call after is `onEventBit`); `getMsg` (.text+0x15C8)
  and `createInit` (.text+0x418C, +0x43AC) read it. So it's set by the pirates' bomb-get scene. The timeline's label
  ("gossip stone text after bombs") differs from that reading; no hint tag on the disc carries 0x0F02 as its flag.
- With the Bombs, the mailbox stocks the Bombs ad (letter 0x7D03, `daObjTpost_c::createInit`,
  `d_a_obj_toripost.cpp:931-933`). Orca's letter (0x7B03) is stocked after 0x1E80 (`:939-941`). Letter registers
  aren't steps.

## The King's two forced talks

- `daShip_c::checkForceMessage` (`d_a_ship.cpp:343-375`) gives the King a message he must say: with the Bombs and
  without 0x1F02 it's 0x624 (`:356-357`); with 0x3E01 and without 0x3F80 it's 0x1688 (`:365-366`). Reading 0x624
  sets 0x1F02 and 0x1688 sets 0x3F80 (`setNextMessage`, `:653-654`, `:665-666`).
- While a forced message is pending, the King's boarding action is removed and he starts the talk when Link is near
  or aboard (`:4204-4215`). Separately, while 0x3E10 is on and 0x3F80 off, he can't be boarded at all (`:4224-4229`).
  So 0x1F02 comes before sailing to Outset, and 0x3F80 before sailing on to Jabun's cave.
- His hints here (`setInitMessage`, `:503-517`): 0xD60 after 0x1F02 (sail home to Outset); with 0x3E10, 0x1687
  before 0x3E01, 0x1688 before 0x3F80, then 0x1689.

## Outset in the Endless Night

- Outset's island tag is `TagIsl` 0x35FF7407 in `sea` room 44's base list: type 7, switch 0x74, event 0x35. Type 7's
  arrival flag is 0x3E10 (`getArrivalFlag`, `d_a_tag_island.cpp:90`), set when its event starts (`demoInitProc`,
  `:133-136`), with switch 0x74 (`actionReady`, `:401-409`). It plays only during the Endless Night and with the
  Bombs (`arrivalTerms`, `:112-127`). Event 0x35 in the sea's `EVNT` list is `PUROLO_RETURN` (Purolo is Outset's
  Japanese name); without the boat it's `PUROLO_RETURN2` (`makeEvId`, `:73`). It doesn't change scene, and the
  developers' stage select has no entry for it.
- 0x3E01: with 0x3E10 on, the player sets it on taking any scene-changing exit (`d_a_player_main.cpp:10800-10804`).
  On the US release, Link arriving aboard the King with 0x3E10 on also sets 0x3E01 and 0x3F80 together
  (`makeBgWait`, `:12462-12467`).
- Catalog 17 ("grandma needs help") sits between: 0x3E10 and 0x3E01 on, 0x3F80 off, restart `sea` 44 point 0.
- Outset's layer here is 4|5 (0x0520), night 2 in the developers' stage select's terms.

## Grandma

- Grandma (`Ba1` type 3) lies sick once 0x0520 is on and until `GRANDMA_HEALED` 0x2A20 (`init_BA1_3`,
  `d_a_npc_ba1.cpp:186-204`). She only reacts to a Fairy in a bottle (`XyCheck_cB`, `:121-125`). Her healing event
  sets 0x2A20 and sends her letter 0x9D03 (`event_proc` case 2, `:1324-1327`); her soup event puts Elixir Soup in a
  bottle (case 1, `:1310-1318`). Catalog 17 -> 18: 0x2A20, the soup and letter 0x9D03 0 -> 1.
- It's a window after `outset_return` with no end: nothing later needs it. The code allows it from 0x0520 on, so a
  heal on an earlier Outset visit (after Farore's Pearl, if the sailing limits allow it) would show as mixed: a
  window can't start in another arc. Bottles aren't checked.

## Catalog

`research/arcs.py`'s `position()` on these steps: 09-16 not started; 17 at `outset_door`; 18-42 at
`korl_outset_talk`, with `heal_grandma` done. None mixed.

## Not placed

- 0x1F04 (Windfall's Endless Night arrival: island tag type 4, switch 0x5B) is part A's; it turns on between 15
  and 16, before the Bombs.
- Between 17 and 18, not this part: 0x1410, 0x1440, 0x2F20, 0x3920 and Nayru's Pearl (part C and after); 0x3008
  (Bomb Bag upgrade, Eastern Fairy Island) and 0x3010 (wallet upgrade on Outset), not the main order.
- Letter registers 0x7A03, 0x7B03, 0x7D03, 0x9D03.
