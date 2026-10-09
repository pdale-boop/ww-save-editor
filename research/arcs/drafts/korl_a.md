# King of Red Lions / Dragon Roost, part A: from the fortress tower to the first sail

Draft for `research/story-flags.md` (to merge). Steps in `korl_a.json`. Covers the flags that turn on between
catalog 45 (on the pirate ship, before the fortress) and 06 (sailing out), after the prologue's last step
`gossip_stone` (0x0520) and before Dragon Roost's arrival flag 0x0902, where part B starts.

## The chain

| # | Step | Flags | Set by | What it gates |
|---|---|---|---|---|
| 1 | `find_sister` | 0x2580 | `FIND_SISTER.stb` (Mjtower), `d_save_event_flag.inc:280` | The Mjtower event `FIND_SISTER` ends with a scene change to Windfall point 200 |
| 2 | `meet_korl` | 0x0F80 `MET_KORL`, 0x2E01 | `MEETSHISHIOH` starting, `d_event_manager.cpp:598-599`; `MEETSHISHIOH.stb`, `d_save_event_flag.inc:354` | The King exists (`d_a_ship.cpp:4548`); saves restart at `sea 11 128` (`l_checkData`, `d_com_inf_game.cpp:1306`) |
| 3 | `sail` | 0x2420, the sail | Zunari's first talk without a sail, `daNpc_Rsh1_c::getMsg`, `d_a_npc_rsh1.cpp:711-716`; his sale, `:1329-1331`; `item_func_normal_sail`, `d_item.cpp:1119-1122` | The sail lesson (`checkForceMessage` needs the sail) |
| 4 | `sail_lesson` | 0x0908 | message 0x5E4, `daShip_c::setNextMessage`, `d_a_ship.cpp:629-630` | Boarding the King (`d_a_ship.cpp:4152-4154`), the sea chart page (`d_menu_collect.cpp:540`), the Up-button map (`d_menu_window.cpp:913`) |
| 5 | `first_sail` | 0x2A08 `RODE_KORL` | the boat's first move with Link aboard, `daShip_c::procPaddleMove_init`, `d_a_ship.cpp:1554-1570` | Saves follow the place again (`d_com_inf_game.cpp:1305`); the hint becomes 0xD5C |

How the pieces connect, from the disc:

- Windfall point 200 is where `FIND_SISTER` leaves Link. Its start event (parameters' top byte 2) is the sea stage's
  `EVNT` entry 2, `MEETSHISHIOH`, with spawn switch 0x0A, so it plays the first time only. `dEvent_manager_c`
  turns on `MET_KORL` when an event with that name starts (`d_event_manager.cpp:598-599`).
- The sea's event list's `MEETSHISHIOH` ends with a scene change to Windfall point 128, standing in the alcove
  beside the King, who is moored there (ship position 0x80) until `RODE_KORL` (`dStage_shipInfoInit`,
  `d_stage.cpp:1933`).
- The King's talk follows `daShip_c::setInitMessage`: no sail gives 0x5DE (`d_a_ship.cpp:382-383`). With the sail
  and 0x0908 off, `checkForceMessage` forces 0x5E0 (`:344-345`), which runs 0x5E1 and 0x5E2; the first answer at
  0x5E2 leads to 0x5E4, which sets 0x0908, the other back through 0x5E3 to 0x5E1 (`:673-688`). This is the
  lesson's loop: the player can hear the explanation again until choosing the first answer.
- `RODE_KORL` is set the first time the boat moves with Link aboard. With 0x0A80 already on (part B's pearl
  hint), the same function also sets 0x1980 (`:1572-1574`), which belongs to the later arc.

The order is the game's: each step's flag is needed for the next (the King only exists with `MET_KORL`, the
lesson needs the sail, boarding needs 0x0908, `RODE_KORL` needs boarding). It agrees with the hint ladder's
first rung (none / 0x0908 / `RODE_KORL`, messages 0x5E0 / 0x5DF / 0xD5C).

The Randomizer's new file sets 0x2E01, 0x0F80, 0x0908 and 0x2A08 together (`asm/patches/custom_funcs.asm:78-84`),
which skips exactly steps 2, 4 and 5 (it gives the sail separately).

## Catalog

| Entry | Restart | 0x2580 | 0x0F80 | 0x2E01 | 0x2420 | 0x0908 | 0x2A08 | Sail | Step |
|---|---|---|---|---|---|---|---|---|---|
| 45 | sea 44 128 | . | . | . | . | . | . | no | before part A |
| 03 | sea 11 128 | x | x | x | . | . | . | no | `meet_korl` |
| 46 [mid-cutscene] | sea 11 128 | x | x | x | . | . | . | no | `meet_korl` |
| 05, 47, 06 | sea 11 0 | x | x | x | x | x | x | yes | `first_sail` |
| 07 | sea 13 0 | x | x | x | x | x | x | yes | part B (0x0902 on) |

Entry 04's folder is empty. No catalog save falls between `meet_korl` and `first_sail`, so the order of steps
3-5 rests on the code, not on saves. The restarts match `dComIfGs_setGameStartStage`: `sea 11 128` while
`MET_KORL` is on and `RODE_KORL` off, then the island's point (Windfall's collision names point 0).

## Left for part B

Between 06 and 07 the catalog turns on 0x0902 (Dragon Roost arrival, `daTag_Island` case 1,
`d_a_tag_island.cpp:84`; landing table `d_com_inf_game.cpp:1275`) together with the Wind Waker, Wind's Requiem and
its learned flag 0x2708. Those come with or after 0x0902, so they belong to part B.

## A note for the editor

`wwedit.evnt_names` reads `EVNT` names from offset 0x04, following the decomp's comment on
`dStage_Event_dt_c::mName` (`/* 0x04 */`). The disc's records have the name at 0x01, right after a one-byte field:
the sea stage's entry 2 reads `TSHISHIOH` at 0x04 but is `MEETSHISHIOH` from 0x01. The decomp's struct
(`u8 field_0x0; char mName[15];`) also puts it at 0x01; only the offset comment differs from my reading. The name
then runs to 0x0F, and `mSpawnSwitchNo` at 0x13 matches (0x0A for this entry).
