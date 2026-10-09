# Jabun arc, part A: the Endless Night to Niko's second rope game

Steps in `jabun_a.json`. Follows the Forest Haven arc (`set_off_farore`, 0x2A02); part B starts with the
Bombs. Sources: the zeldaret/tww decomp, the disc (actor lists, island tags, event names), the compiled
modules (`research/scratch/findli.py`, `relcalls.py`), and the catalog's flag timeline (15 -> 16).

| # | Step | Flags, switches | Evidence |
|---|---|---|---|
| 1 | `endless_night` | `ENDLESS_NIGHT` 0x0A02; sea switch 0x19 | Island tag type 3 in sea room 23 (Greatfish Isle), event `ARRIVAL_BRK`: `daTag_Island_c::getArrivalFlag` and `demoInitProc` (`d_a_tag_island.cpp:82-92, 133-135`); switch in `actionReady` (`:399-406`) |
| window, after 1 | `quill_sunken_island` | 0x1E80 | Quill type 4 in sea room 23, event `Skn_Islnd`; its end sets the flag (`d_a_npc_bm1.cpp:503-508, 586-592, 2994-2998`) |
| 2 | `korl_endless_night` | 0x0A01 | Message 0x607 while the night lasts and 0x0A01 is off (`d_a_ship.cpp:353-355`); reading it sets 0x0A01 (`:647-648`) |
| 3 | `set_off_endless_night` | 0x2A01 | `daShip_c::procPaddleMove_init` with `ENDLESS_NIGHT` on (`d_a_ship.cpp:1580-1581`) |
| 4 | `windfall_endless_night` | 0x1F04 (0x1F01 optional); sea switch 0x5B | Island tag type 4 on Windfall's layers 2 and 3, event `ARRIVAL_TWN`, only during the Endless Night (`arrivalTerms`, `d_a_tag_island.cpp:116-120`) |
| 5 | `password_cutscene` | 0x2110, 0x3B20 | Event tag type 9 in the bomb shop (`Obombh`): start sets 0x3B20 and picks the password into event register 0xBA0F, end sets 0x2110 (`d_a_tag_event.cpp:108-120, 145-146`); `bombshop.stb` also sets 0x2110 |
| 6 | `password_door` | 0x1910 | The pirate ship's deck door is created by the ship with door type 4 (`d_a_obj_pirateship.cpp:214, 253`); right password needs 0x2110 and sets 0x1910 (`d_a_knob00.cpp:172, 630-633`) |
| 7 | `niko_rope_2` | 0x1A04 | Compiled `d_a_npc_p2.rel`: set in `daNpc_P2_c::demo_intro_2`, read in `intro_action` and `createInit` |

## Notes

- **Where the Endless Night starts.** Greatfish Isle's island tag (parameters 0x05FF1903: event 5
  `ARRIVAL_BRK` in the sea's `EVNT` list, switch 0x19, type 3) sets `ENDLESS_NIGHT` when its arrival
  scene starts. Its `arrivalTerms` has no story condition for type 3 beyond the flag being off; in play
  the King's mark after Farore's Pearl leads there. `dKy_checkEventNightStop` (`d_kankyo.cpp:3161-3167`)
  holds the night until Nayru's Pearl.
- **Quill.** Quill type 4 is in Greatfish Isle's base actor list and only appears while 0x1E80 is off
  (`init_PST_4`). His event `Skn_Islnd` sets 0x1E80 at its end. Nothing later found requires the flag, so
  it is a window after `endless_night` with no end.
- **The King of Red Lions.** Rung 6 of his hint ladder: message 0x607 (Jabun survived) sets 0x0A01 when
  read; moving the boat during the night sets 0x2A01. After Windfall's arrival, 0x1F04 changes his hint
  to 0x621 (see what the pirates are doing) and, once 0x2110 is on and there's no Bomb Bag, 0x623 (the
  password reminder) (`d_a_ship.cpp:519-529`). Message 0x622 sets 0x1F01 (`:650-651`), never on in the
  catalog, so it is optional.
- **Windfall during the night.** The arrival tag is on layers 2 and 3 only, which Windfall uses during
  the Endless Night (`getLayerNo`; the developers' stage select names layer 3 "pirates"). Type 4's
  `arrivalTerms` also requires `dKy_checkEventNightStop`.
- **The password.** The bomb shop (`Obombh` room 0) has Tetra and three pirates on both layers and an
  event tag (`TagEv`, type 9). Its start sets 0x3B20 (if off) and stores a random password number 0-5 in
  event register 0xBA0F, then the password text; its end sets 0x2110. Talking to the password door before
  the cutscene also sets 0x3B20 and picks the number (`actionPassward2`, `d_a_knob00.cpp:609-611`), so
  0x3B20 alone doesn't mean the cutscene ran.
- **The password door is the pirate ship's.** No door on the disc is placed with type 4. The pirate ship
  actor (`Pirates`, `daObj_Pirateship`) creates its deck door in code with `dr_prm[door byte]`:
  0x101000FF (type 0) or 0x101004FF (type 4, the password door). On Windfall's layers 2 and 3 the ship has
  door byte 1; on Outset's layers it has 0. The door stays locked until 0x1910
  (`d_a_knob00.cpp:710-714`), which the right password sets.
- **Niko.** `d_a_npc_p2` is "Zuko, Niko and Mako". 0x1A04 has no setter in the decomp source; in the
  compiled module it is set in `demo_intro_2` (his intro to the second rope game). Niko (`P2b`, parameters
  0x00030005) is in the pirate ship's interior (`Asoko`) on layers 2 and 3, used after 0x0520.

## Catalog

| Entry | Position on these steps |
|---|---|
| 15 | not started |
| 16 ("niko's trial numero dos pre win") | `niko_rope_2` (all done, window done) |
| 17, 18, 41 | `niko_rope_2` |

Restarts: 16 holds `sea 11 0`; a save at Greatfish Isle would restart at `sea 23 0` (the island's
restart number on the disc).

## Unplaced

No flags. Event registers that change between 15 and 16 and aren't placed: 0xBA0F (the password number),
0x7B03 and 0xB503 (letters), 0xAB03 and 0xCF03 (1 -> 3, not identified).
