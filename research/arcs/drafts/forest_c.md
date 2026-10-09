# Forest Haven arc, part C: after Kalle Demos to setting off with Farore's Pearl

Steps in `forest_c.json`. Decomp paths are in the zeldaret/tww clone; disc data was read with `wwedit`
(event lists, `EVNT` chunks, spawn points). The catalog has no save between 15 (inside the Forbidden Woods)
and 16 (Niko's trial, already in the next arc), so 15 and 16 bound everything here and the order comes from
the code.

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `farores_pearl` | Farore's Pearl; area 11 switch 0x0D | Boss warp (`daWarpf_c`) → `WARP_WIND` → `Omori` point 214 → `getperl_deku` → `getperl_deku.stb` (item payload 4) |
| 2 | `leave_forest_haven` | 0x1C40 | An `Omori` room unloading while Link has Farore's Pearl (`d_s_room.cpp:271-272`, `:134-135`) |
| 3 | `korl_farore_talk` | 0x0A08 (0x0A04 optional) | Forced message 0x5F6 → 0x5F7, which sets 0x0A08 (`d_a_ship.cpp:350-351`, `:693-694`, `:641-642`) |
| 4 | `set_off_farore` | 0x2A02 | The boat moving with 0x0A08 on (`daShip_c::procPaddleMove_init`, `:1576-1577`) |

## 1. The warp and Farore's Pearl

- The warp in Kalle Demos's room is `daWarpf_c` (`d_a_warpf.cpp`). `CreateInit` (:267-279) refuses to
  appear until the stage's boss is beaten (`dComIfGs_isStageBossEnemy()`), then picks `WARP_WIND` unless
  `checkEndDemo` is true; for the Forbidden Woods' save table (`STAGE_FW`) that is "Farore's Pearl owned"
  (:224-227). After the pearl it plays `WARP_WIND_AFTER`.
- `kinBOSS`'s event list: `WARP_WIND` has a `Cb1` staff (Makar: `TO_LINK`, `WARP`), so Makar warps out with
  Link, and its `DIRECTOR` ends with `NEXT` to `Omori` room 0, start code 214. `WARP_WIND_AFTER` has no
  Makar and goes to start code 215.
- `Omori` point 214 has parameters 0x01FF0000: start event 1 of `Omori`'s `EVNT` list, `getperl_deku`
  (point 215: event 2, `BOSS_WARPOUT`; point 213: event 0, `meet_deku`, part A's).
- `Omori`'s `EVNT` entry for `getperl_deku` has spawn switch 0x0D. `dEvent_exception_c::setStartDemo` plays
  a spawn event only while its switch is off and turns it on (`d_event_manager.cpp:41-48`). `Omori`'s `STAG`
  save table is 11, so the switch is saved in area 11 (the area all save-table-11 stages share; part B of
  the Dragon Roost arc uses switches 0x08-0x1F there for Dragon Roost's stages, none of them 0x0D).
- `getperl_deku`'s `PACKAGE` staff plays `getperl_deku.stb` (`Stage` `Omori`, `StartCode` 214, so it ends
  where it began). Its demo data gives item payload 4, Farore's Pearl (`d_a_demo00`'s item table, read in
  `research/story-flags.md`).
- Catalog: Farore's Pearl and the switch are off in 15 and on in 16, 17 and 41.

The Koroks' ceremony and the Deku Tree handing over the pearl are what the cutscene shows as far as I know
the story; the `.stb`'s camera and actor tracks weren't read.

## 2. Leaving Forest Haven: 0x1C40

`dScnRoom_Create` records `field_0x1dc = 2` when the stage is `Omori` and Link has Farore's Pearl
(`d_s_room.cpp:271-272`); `dScnRoom_Delete` sets 0x1C40 when a room with that mark unloads (:134-135). So it
is set when Link leaves Forest Haven's interior with the pearl. The timeline's note ("after talking to the
Deku Tree after Farore's Pearl, new Deku Tree text") adds a talk that the code doesn't require; that note
differs from my reading of the code. Off in 15, on in 16.

## 3. The King's talk: 0x0A08, 0x0A04

- `daShip_c::checkForceMessage` forces message 0x5F6 when Farore's Pearl is owned
  (`dComIfGs_isSymbol(dSymbol_FARORE_e)`) and 0x0A08 is off (`d_a_ship.cpp:350-351`). 0x5F6 continues to
  0x5F7 (:693-694), and `setNextMessage` sets 0x0A08 on 0x5F7 (:641-642).
- With 0x0A08 on and 0x2A02 off, the King's hint is 0x5F8, or 0x5F9 once 0x0A04 is on (:545-555); reading
  0x5F8 sets 0x0A04 (:644-645). That needs a second talk before setting off, and no catalog save has it:
  optional.
- 0x2B80 (message 0x5F4, Forest Haven's arrival hint) belongs to part A.

## 4. Setting off: 0x2A02

`daShip_c::procPaddleMove_init` sets 0x2A02 when the boat starts moving with Link aboard and 0x0A08 is on
(`d_a_ship.cpp:1576-1577`), next to `RODE_KORL` and 0x1980 (:1569-1574). From then the hint is 0xD5E
("hurry to the mark", :545-547). Off in 15, on in 16.

## Restart

Saving in `Omori` (save table 11) writes point 0 of its sea square from the stage's map info
(`dComIfGs_setGameStartStage`, `d_com_inf_game.cpp:1376-1385`): `sea` 41 point 0, which catalog 11-14
(saved in Forest Haven) hold. After setting off it follows the place; catalog 16 holds `sea` 11 0.

## Catalog

| Entry | Position on these steps |
|---|---|
| 10, 11, 13, 14, 15 | not started |
| 16, 17, 41 | `set_off_farore` (done) |

## Not part C

From the 15 → 16 changes: 0x3D40 (Kalle Demos defeated, `dMeter_recollect_boss_data`,
`d_meter.cpp:1075-1077`), the Boomerang, the heart container and event register 0xA107 (1 → 7; by analogy
with Dragon Roost Cavern's 0xA207, probably the Forbidden Woods' warp pots, not checked) are part B. 0x0A01,
0x0A02 (`ENDLESS_NIGHT`), 0x1910, 0x1A04, 0x1E80, 0x1F04, 0x2110, 0x2A01 and 0x3B20 are the Endless Night
and Windfall, the next arc.
