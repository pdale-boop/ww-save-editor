# Tower of the Gods arc, part C: Hyrule and the Master Sword

From the warp down from the Tower of the Gods' bell to the battle in Hyrule Castle after the Master
Sword. Leaving Hyrule (0x3810, `daWarphr_c`) is the next arc's first step. Steps in
`tower_c.json`. Sources: the decomp (zeldaret/tww), the disc's event lists, spawn points, actor
lists and `.stb` payloads, compiled modules where the decomp is Nonmatching, the catalog's flag
timeline (19 -> 20), and the developers' stage select (group 32, with the BlueWake session's
English names).

All three stages (`Hyrule`, `Hyroom`, `kenroom`) have save table 9, so their saved switches share
area 9 and saving in them restarts at the stage's exit 0: `Hyrule` 0 0, `Hyroom` 0 10, `kenroom`
0 10. Catalog 20 has area 9 switches 0x02, 0x04, 0x06, 0x0B, 0x0C, 0x0D, 0x0E, 0x10 and 0x12; all
but 0x10 are placed below.

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `hyrule_arrival` | 0x2D10; switch 0x02 | ADMumi's `warp_in`: `EventFlag` 11536 (0x2D10), then `Hyrule` point 200, layer 8. That point starts `warp_out` (spawn switch 0x02), which goes to point 201, layer 0 (`daWarphr_c`, `d_a_warphr.cpp:171`). Ladder rung 14: with 0x2D10 and no Master Sword the King says 0xD65 and can't be boarded (`d_a_ship.cpp:362-363, 483-484, 4224-4229`) |
| 2 | `castle_intro` | switch 0x12 | `Hyroom` point 0 starts `hy_intro` (EVNT 2, spawn switch 0x12) |
| 3 | `triforce_statue` | switch 0x06 | The Link statue `YLzou` (parameters 6 = its saved switch) slides aside once switch 6 is on (`daObjYLzou_c::set_start_type`, `d_a_obj_YLzou.cpp:99-105`). The triangle blocks `MtryB`/`MtryBCr` carry 6 in bits 8-15; `d_a_obj_tribox` is Nonmatching |
| 4 | `master_sword` | 0x2D04; switches 0x0E, 0x0B | The hint tag (`TagHt2` 0xFFFF0E4A, type 0x0A) sets 0x0E when it starts (`daTag_Hint_c::startProc`, `d_a_tag_hint.cpp:443-460`). The event tag (`TagEv` 0x000E0BFF) then plays event 0, `master_sword`, and sets 0x0B (`d_a_tag_event.cpp:51-72, 218-229`). `master_sword`: `EventFlag` 11524 (0x2D04), then `Hyroom` point 248, layer 8. The pedestal sword `VmsMS` deletes itself (`d_a_obj_vmsms.cpp:74-80`) |
| 5 | `colors_return` | `COLORS_IN_HYRULE` 0x3802; switch 0x0C | `Hyroom` point 248 starts `rebirth_hyral` (spawn switch 0x0C). `rebirth_hyral.stb` (Demo49.arc) has flag payload 0x31 = `COLORS_IN_HYRULE` (`d_a_demo00.cpp:702`). It ends at `kenroom` point 249, layer 10 |
| 6 | `swing_sword` | 0x3A04; Master Sword (Powerless); switch 0x0D | `kenroom` point 249 starts `swing_sword` (spawn switch 0x0D): `EventFlag` 14852 (0x3A04), then point 249, layer 6. `swing_sword.stb` (Demo50.arc) has item payload 0 = `dItemNo_MASTER_SWORD_1_e` (`d_a_demo00.cpp:715`). Ladder rung 15: with the sword equipped the King says 0xD66 (`d_a_ship.cpp:480-481`) and can be boarded again |
| 7 | `castle_battle` | 0x3B40; switch 0x04 | `COLORS_IN_HYRULE` wakes the Darknut and Moblin statues on `Hyroom`'s layers 0\|1 (`d_dozou`, `d_a_tn.cpp:2321-2326`; `d_a_mo2.cpp:2712`). The trap `TnTrap` appears once 0x3A04 is on and sets 0x3B40 (compiled `d_a_obj_tntrap.rel`: `chk_appear` .text+0x118, `chk_event_flg` .text+0x938; the decomp's version is Nonmatching). `ALLdie` (0xFFFF04FF) sets switch 4 when no enemy is left (`d_a_alldie.cpp:36-47`). Then `Hyroom` loads layer 6\|7 (`getLayerNo`, `d_com_inf_game.cpp:234`) |

The developers' stage select has the same chain as cutscene starts: `kenroom` 200 layer 8
"Before Master Sword", `Hyroom` 248 layer 8 "Taking Master Sword", `kenroom` 249 layer 10 "After
Master Sword", `Hyrule` 200 layer 8 (group 32 entries 22, 45, 46, 41).

Order: steps 4-6 are one chain of events (each ends where the next one's spawn point is). Step 7
needs 0x3A04 for the trap and `COLORS_IN_HYRULE` for the enemies. Step 3 comes before 4 because the
way to the chamber is under the statue.

Catalog (`arcs.position` on these steps): 01-19 not started, 20-42 at `castle_battle` (done),
crafted 50 and 51 mixed (Master Sword given without the flags). No game-written save is mixed. No
catalog save falls inside this stretch, so the order rests on the chain above.

Not settled:
- `0x2D10` is set when the bell's warp (`warp_in`) starts, which may also be part B's last step.
- Area 9 switch 0x10 (on in 20) has no actor tied to it yet.
- What `TnTrap` checks before setting 0x3B40 (switch 4 or its own enemy check) isn't read; only
  compiled code has it.
- `MtryB`'s switch 6 is read from its parameters; its code is Nonmatching.
