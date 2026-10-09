# Tower of the Gods arc, part A: the pearls and the tower rising

From Nayru's Pearl (the Jabun arc's last step, `jabun_pearl`) to the tower standing and the King of Red Lions'
next talk. Parts B (the Tower of the Gods dungeon) and C (Hyrule and the Master Sword) follow. Steps are in
`tower_a.json`.

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `korl_nayru_talk` | 0x2F20 | Forced message 0xD5A with Nayru's Pearl owned (`daShip_c::checkForceMessage`, `d_a_ship.cpp:359-360`); 0xD5A → 0xD5B (`:696-697`) sets 0x2F20 (`:656-657`). The King can't be boarded while it's pending (`:4204-4205`) |
| window, by 4 | `place_din` | 0x1480 | Statue 0 on `sea` 18 (Northern Triangle Island) |
| window, by 4 | `place_farore` | 0x1440 | Statue 1 on `sea` 27 (Eastern Triangle Island) |
| window, after 1, by 4 | `place_nayru` | 0x1410 | Statue 2 on `sea` 32 (Southern Triangle Island) |
| 4 | `tower_raised` | 0x1E40, 0x2E80 | The third statue sets 0x1E40 and plays `MEGAMI_DEMO` (`d_a_obj_doguu.cpp:737-739`) → `ADMumi` point = that statue's number, layer 8 (`setJDemo`, `:355`) → `towerd`/`towerf`/`towern.stb` set 0x2E80 and end at `sea` 26 point 0, in the boat |
| 5 | `korl_tower_talk` | 0x3840 | Aboard, with 0x1E40 on: message 0x168C (`d_a_ship.cpp:4234-4235`) sets 0x3840 (`:669-670`) |

## The statues (`d_a_obj_doguu`, `daObjDoguu_c`)

- Which statue is which: its number is the low byte of its parameters (`d_a_obj_doguu.cpp:530-532`), and the
  number picks the pearl (`CreateInit`, `:199-205`): 0 Din, 1 Farore, 2 Nayru. On the disc the statues are on
  `sea` 18 (0x0000FF00), 27 (0x0000FF01) and 32 (0x0000FF02), in each room's base actor list, so on every layer.
- Placing: the statue reacts only while its pearl is owned and Link touches it (`checkItemGet(mItemNo, TRUE)`,
  `:673`). It plays `DOGUU_DEMO1`, then `DOGUU_DEMO2` only for the first pearl placed of the three (`:699`), then
  `DOGUU_DEMO3`, and sets its `PLACED_*` flag (state 9, `:734-735`; `setFinishMyEvent`, `:511-518`).
- No story check besides the pearl. Din's and Farore's statues can be done as soon as those pearls are owned, so
  their windows have no start. Nayru's needs the boat, which the forced talk blocks until 0x2F20.
- The pearls stay in the inventory: the statue code clears no pearl bit, and catalog 18-42 keep all three.
- The third pearl, whichever it is, sets 0x1E40 and orders `MEGAMI_DEMO` (`:737-739`). That cutscene's jump goes
  to `ADMumi` room 0, layer 8, at the point numbered like the statue (`dComIfGp_setNextStage("ADMumi",
  field_0x894, 0, 8)`, `:355`). The developers' stage select (bench folder, group 32, entries 18-20) names these
  "Tower rises D", "F" and "N": `ADMumi` points 0, 1 and 2, layer 8. `ADMumi`'s event list has `towerd`, `towerf`
  and `towern`, each ending with a scene change to `sea` room 26 point 0 (a boat arrival). 0x2E80 is set by
  `towerd.stb`, `towerf.stb` and `towern.stb` (`d_save_event_flag.inc:347`).

## Hazard for crafted saves

With all three `PLACED_*` flags on, every statue loads in its finished state (`CreateInit`, `:223-234`, state 14)
and never reaches the code that sets 0x1E40. So setting the three flags without 0x1E40 leaves the tower down with
no way to raise it. Set 0x1E40 together with the third flag (and 0x2E80, which the cutscene would set).

## Catalog

| Entries | Position | Windows |
|---|---|---|
| 15-17 | not started | none placed |
| 18 | `korl_nayru_talk` | Farore and Nayru placed, Din not |
| 19-42 | `korl_tower_talk` | all three placed |

None mixed. Checked with `research/arcs.py`'s `position()` (the main checkout's copy, which supports windows
without a start).

## Restart

Saving on a Triangle Island restarts at that island's point 0 (`sea` 18, 27 or 32 point 0: the island point from
the ground's restart number, which is 0 on each; `wwedit.disc_restart_places`).

## Not placed

Also on from catalog 17 to 18, belonging elsewhere: 0x2A20 (Grandma healed; the Jabun arc's `heal_grandma`
window), 0x3920 and 0x3F80 (the Jabun arc), 0x3008 (Bomb Bag upgrade, Eastern Fairy Island) and 0x3010 (wallet
upgrade, Outset), and letter registers 0x7A03 and 0x9D03.
