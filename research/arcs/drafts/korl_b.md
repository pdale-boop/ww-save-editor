# King of Red Lions arc, part B: Dragon Roost Island up to the cavern

Draft for merging into the arc (2026-10-09). Steps are in `korl_b.json`. Part A ends where the arrival
starts; part C starts inside Dragon Roost Cavern. Decomp references are zeldaret/tww; "compiled" means
read from the game's compiled module with `research/scratch/findli.py`, `relcalls.py` and `niko.py`.
Disc data was read from the stages' `.dzr`/`.dzs` and `event_list.dat` with throwaway scripts in the
session scratchpad (same layouts as `wwedit`).

## Order and evidence

1. **Arrival and the Wind Waker** (`0x0902`, Wind Waker, sea switch 0x0B). One tag drives the whole
   sequence: `TagIsl` in sea room 13, parameters 0x03FF0B01 (type 1, switch 0x0B, event 3 = `ARRIVAL_DRG`).
   `daTag_Island_c::getArrivalFlag` gives 0x0902 for type 1 (`d_a_tag_island.cpp:84`), set when the arrival
   starts (`demoInitProc`, :135), and the tag's switch is set at the same time (`actionReady`, :408). When the
   arrival ends, `actionEvent` starts the conducting lesson `TACT_TEARCH0` (:386); `demoProcTact_Af` repeats
   it (`TACT_TEARCH1`, `2`, `4`) until `TACT_TEARCH3` (:230-245), whose Link cut `011get_item` has prm0 34,
   the Wind Waker (sea `event_list.dat`). 0x0902 is also Dragon Roost's landing event
   (`dComIfGs_checkSeaLandingEvent`, `d_com_inf_game.cpp:1275`), so from here a save on the island restarts
   at the island's point 0, and the ship stops enforcing its first range path (`d_a_ship.cpp:1020`).
   Optional: 0x0A10, set by reading the King's hint 0x5EA (`daShip_c::setNextMessage`, `d_a_ship.cpp:632`).
2. **Wind's Requiem** (`0x2708`). `daNpc_Hr_c::demoProcTact1` (`d_a_npc_hr.cpp:485`); the Hr actor
   (Zephos, type 0) stands in sea room 13. His lesson checks the Wind Waker on a button (:250), so it follows
   step 1. 0x2708 is `wwedit.SONG_FLAGS`' flag for the Wind's Requiem.
3. **Quill on the island** (`0x1F40`). `daNpc_Bm1_c` type 2 shows only while 0x1F40 is off
   (`init_PST_2`, `d_a_npc_bm1.cpp:566`); its event `Met_Ryu_Islnd` sets 0x1F40 and removes him
   (`event_proc`, :2989). Steps 2 and 3 can happen in either order as far as the code shows.
4. **The Rito Aerie** (`0x2502`, Delivery Bag, area 11 switch 0x09). `TagEv` in `Atorizk` room 0,
   parameters 0x00FF0908: type 8, switch 0x09, event 0 `demo10` = `dragontale.stb`. Type 8 sets 0x2502
   when the event ends (`daTag_Event_c::demoEndProc`, `d_a_tag_event.cpp:140`). The Delivery Bag is on in
   catalog 07, but no event list gives item 0x30; who gives it is open (possibly the `.stb`).
5. **The Father's Letter** (`0x0E02`). Medli in the aerie: first message 0x17D5; 0x17D8 starts
   `Md_ItemGet`, which gives item 0x98 (`initialLetterEvent`, `d_a_npc_md.cpp:3535, 3543`); 0x17DB sets
   0x0E02 (:5095).
6. **Komali gets the letter** (`0x0F04`, `0x1810`; `0x0F08` optional). Komali (`Co1`, `Comori` room 0)
   isn't decompiled. In the compiled module, `talk_1` checks `dNpc_chkLetterPassed`, sets 0x0F08 and
   0x0F04 and takes the letter (`CancelPresent`, `setReserveItemEmpty`); `event_proc` sets 0x0F04 and 0x1810
   when its event ends; `wait_action1` checks `dNpc_chkLetterPassed` and 0x1810. `dNpc_chkLetterPassed`
   (`d_npc.cpp:647`) is: Delivery Bag ever-held bit 0xC on, and the letter no longer in the bag.
7. **Medli at the cavern's entrance** (`0x1104`). She appears at `Adanmae` only after the letter is passed,
   and leaves the aerie at the same time (`d_a_npc_md.cpp:577-583`, create). Talk 0x17E6-0x17F1 leads to her
   event `md_cliff` (:5163); 0x17F4 sets 0x1104 (:5170).
8. **The bottle** (`0x1102`). Thrown onto the ledge (ground height 600-700 in her camera tag),
   `chkAdanmaeDemoOrder` starts `MD_FLY` (:1484), which gives item 0x50, the Empty Bottle (:3539, 3543);
   0x1801 sets 0x1102 (:5198).
9. **Water for the bomb flowers** (area 11 switches 0x08, 0x1A-0x1D, 0x1F). `Eskban`, a bombable rock over
   the `Ygush01` springs, sets switch 0x08 when it breaks (`d_a_obj_eskban.cpp:353-354`). The five `VbakH`
   bomb flowers are kind 1, dead; water brings one to life and sets its switch
   (`d_a_bflower.cpp:421-425`). Catalog 08 holds a Water Bottle (0x56).
10. **The statues** (area 11 switches 0x0E, 0x0F, 0x18). `Ebomzo`, "bombable statues (outside Dragon Roost
    Cavern entrance)", set their switches when destroyed (`d_a_obj_ebomzo.cpp:136`). The `TagEv` with
    parameters 0x020F18FF waits for 0x0F, plays `RiddleSound0` and sets 0x18 (`d_a_tag_event.cpp:54-73, 228`).

Saving anywhere on this stretch restarts at `sea 13 0`: the island's point 0 on the sea once 0x0902 is on,
and point 0 of the sea square for `Atorizk`, `Comori` and `Adanmae` (`wwedit.disc_restart_places`). Catalog
07 and 08 hold `sea 13 0`.

## Catalog check

With `arcs.step_missing` and `arcs.position` on the draft's steps alone: catalog 05 and 06 are at step 0,
07 at step 6 (letter delivered), 08 at step 9 (flowers watered), 09, 10, 11 and 41 at step 10. No save is
mixed.

## For merging

- **A new key, `delivery_passed`.** Step 6 depends on the letter having been delivered, which is save data
  but not a flag: the Delivery Bag's ever-held bits (`RESERVE_FLAGS`, bit = item - 0x8C) with the item gone
  from the bag. `arcs.py` ignores the key for now; checking it would need a reader in `arcs.py`.
- **Songs and bottles aren't checkable by `arcs.py`**: the Wind's Requiem goes with 0x2708, the bottle with
  0x1102.
- **Unplaced:** the Delivery Bag's giver; the Piece of Heart between catalog 06 and 07; event register
  0x7EFF (14 -> 12); sea switches 0x24, 0x41, 0x43, 0x45, 0x6F, 0x73 (on between 06 and 07, other squares).
- **Outside this part, found on the way: `wwedit.evnt_names` reads the names 3 bytes late.** Event names in
  a stage's `EVNT` chunk start at offset 1 of each 0x18-byte entry, not 0x04 as the decomp's
  `dStage_Event_dt_c` comment has it: read at 0x04, the sea's names come out as `IVAL_DRG`,
  `perl_komori`, `LENSISTER` instead of `ARRIVAL_DRG`, `getperl_komori`, `STOLENSISTER` (checked by reading
  the sea's list at offset 1). The editor's spawn-point event labels use that function, so Windfall point
  200's start event, index 2, is `MEETSHISHIOH`, not "TSHISHIOH" as labeled today. The spawn-switch byte at
  0x13 reads right: `ARRIVAL_DRG` has 0x0B, the arrival tag's switch.
