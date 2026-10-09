# Forest Haven arc, part A: the arrival to the way into the Forbidden Woods

Steps in `forest_a.json`. Starts right after the King of Red Lions arc's last step (`south_wind`); ends
where part B (the Forbidden Woods) begins: catalog 14, on a platform outside Forest Haven before the updraft.

## Order and evidence

1. **Arrival** (`0x0A20`, sea switch 0x1A; optional 0x2B80). `TagIsl` in sea room 41, parameters 0x06FF1A02:
   type 2, switch 0x1A, event 6 of the sea's `EVNT` list, `ARRIVAL_FST`. `daTag_Island_c::getArrivalFlag`
   gives 0x0A20 for type 2 (`d_a_tag_island.cpp:85`); `demoInitProc` sets it (:133-135) and `actionReady`
   the switch (:407-408). 0x0A20 is Forest Haven's landing event (`l_landingEvent`, `d_com_inf_game.cpp:1277`),
   so from here a save on the island restarts at the point the ground names (room 41's collision names only
   0); saves inside `Omori`, `Ocrogh` and `Otkura` restart at sea 41 point 0 (save table 11). The King's hint
   ladder, rung 4: 0x5F4, then 0x5F5 once 0x2B80 is set, 0x5F6 with Farore's Pearl
   (`daShip_c::setInitMessage`, `d_a_ship.cpp:558-569`); reading 0x5F4 sets 0x2B80
   (`daShip_c::setNextMessage`, :638-639). 0x2B80 never turned on in the playthrough and only changes the
   hint, so it is optional.
2. **The Deku Tree** (`0x1801`). Not set anywhere in the decomp's source; in the compiled
   `d_a_npc_de1.rel` it is set in `daNpc_De1_c::checkOrder` (.text+0xF00, `onEventBit`) and read in
   `createInit` and `setMtx` (`findli.py`, `relcalls.py`). The Deku Tree (`De1`) stands in `Omori` room 0
   (layers 0, 1, 10, 11); its first cutscene is the stage event `meet_deku`, which ends at `Omori` point 213.
   Readers: the Deku Leaf actor spawns only with it (`daDekuItem_c::_create`, `d_a_deku_item.cpp:116-118`),
   Baba Buds of type `APPEAR_AFTER_DEKU_TREE` turn normal with it (`daJBO_Execute`, `d_a_jbo.cpp:124-128`),
   a type-9 hint tag stops with it (`d_a_tag_hint.cpp:178-180`), and four Korok types read it when they set
   up (`init_BJ4_0`, `init_BJ6_0`, `init_BJ7_0`, `init_BJX_0`). The timeline's note says it is set on the
   last parasite's death, which fits `checkOrder` ordering the tree's event afterwards (not traced).
3. **The Deku Leaf** (item; magic 16). `itemDek` at the top of the tree (`Omori` room 0, layers 0 and 1,
   parameters 0x2: item bit 2, y 5035): spawns after 0x1801 and not once its item bit is set
   (`d_a_deku_item.cpp:110-118`), gives item 0x34 (:203). `item_func_deku_leaf` gives the leaf and the
   magic meter, max 16 (`d_item.cpp:810-815`). Catalog: between 11 and 12 (both mid-cutscene).
4. **A Korok calls Link** (`0x2902`; optional 0x0C02). `daNpc_Bj1_c::event_proc` sets 0x2902
   (`d_a_npc_bj1.rel` .text+0x48C4) and `wait_4` reads it (+0x4E98). 0x0C02 is a Korok's first talk
   (`talk_1`, +0x5378), read by `getMsg_BJ6_0` (+0x2040): the `Bj6` Korok (on a ledge at y 3383 in `Omori`),
   named Rown in the timeline. Nothing found requires it, so optional. Catalog: 0x2902 between 12 and 13,
   0x0C02 between 13 and 14.

Catalog 14 (the updraft) adds nothing checkable: the first flag of the Forbidden Woods (0x2B20, the first
door flower) is part B's.

## Proposed for the King of Red Lions arc: the Song of Passing

`0x0B08` is Tott's first talk (`daNpc_Tt_c::getMsg`, `d_a_npc_tt.cpp:163-167`); with it and without
`0x0C40` he orders his dance-along (:624-626); conducting along sets `0x0C40` (`demoProcTact1`, default
branch, :320), so it needs the Wind Waker; afterwards he only dances (`setAnmStatus`, :73). Tott is on
Windfall (sea room 11) on layers 0, 1, 4 and 5. Catalog: both first on between 10 and 11. It can be done any
time after the Wind Waker (the King of Red Lions arc's `dri_arrival`) and nothing found needs it later, so
the draft proposes it as a windowed step of that arc (`window: {"after": "dri_arrival"}`, no end), with the
song checked (`songs`).

## Not placed

- `0x1E10`: Gillian's (`NPC_UW1`) first talk at night (`d_a_npc_people.cpp:6992-6994`); her later talks
  branch on the Delivery Bag and the Magic Armor. `0x2304`: Loot's (`NPC_SA1`) first talk (:7158-7160).
  Both first on between 10 and 11; they start Windfall chains of their own, not steps here.
- Also between 10 and 11, not this part: an Empty Bottle in slot 15, Gohma's heart container (3.25 -> 4.25),
  event registers 0xAB03 and 0xCF03 (0 -> 1) and 0x7EFF (12 -> 0).

## Catalog check

`arcs.position` on these four steps: 09 and 10 not started; 11 `deku_tree` (leaf not yet given,
mid-cutscene); 12 `deku_leaf`; 13 to 42 `korok_leaf_scene`. None mixed. The Song of Passing step is done in
11 onward.
