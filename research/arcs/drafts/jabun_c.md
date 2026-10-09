# Jabun arc, part C: Jabun's cave and Nayru's Pearl

From the stone wall at Jabun's cave on Outset to Nayru's Pearl and the end of the Endless Night. Starts once
the bombs are in hand (part B); ends before the King of Red Lions' talk that sets 0x2F20 (rung 12, the
pearl-placing arc). Step list: `jabun_c.json`.

| # | Step | Sets | Evidence |
|---|---|---|---|
| 1 | `jabun_slab` | area 0 switch 0x1C; 0x1940 optional | The wall `Ajav` (`daObjAjav`) on Outset's layers 5 and 7, broken by bombs in three stages (`ajav_destroy0`, `ajav_destroy1`, `ajav_uzu`); the last turns its switch 0x1C on (`d_a_obj_ajav.cpp:823`). 0x1940: caught by the whirlpool (`daShip_c::procWhirlDown`, `d_a_ship.cpp:2887-2893`) |
| 2 | `jabun_pearl` | 0x3920; Nayru's Pearl | `ajav_uzu` → `Pjavdou` point 200, layer 8 → `getperl_jab` (`getperl_jab.stb`, `EventFlag` 0x3920, item payload 5 = Nayru's Pearl) → `sea` 44 point 9 |

Restart: on Outset after the first sail, the island point under Link, `sea 44 0` (catalog 17); in Jabun's cave
(`Pjavdou`, save table 11), point 0 of its sea square, also `sea 44 0`.

## The wall and the whirlpool

- `Ajav` ("Stone wall blocking the entrance to Jabun's cave") stands at (-205542, 0, 324297) in `sea` room 44's
  `ACT5` and `ACT7`, parameters 0x1C. It exists only while `ENDLESS_NIGHT` is on and its switch (parameters &
  0xFF = 0x1C, in its home room) is off (`_create`, `d_a_obj_ajav.cpp:470`; `check_ev`/`check_sw`,
  `d_a_obj_ajav.h:74-76`).
- Its hit spheres take bombs (`AT_TYPE_BOMB`, `d_a_obj_ajav.cpp:50, 79, 109`). Each hit runs the next of
  `ajav_destroy0`, `ajav_destroy1`, `ajav_uzu` (`l_daObjAjav_ev_name`, `:153-157`; `to_broken`, `:617-623`);
  after the last it turns switch 0x1C on (`:823`). The sea saves to area 0, so the switch is saved.
- The boat's cannon fires real bombs: with the Bomb Bag item on a button while sailing, `daShip_c` creates a
  `daBomb_c` and uses one up (`d_a_ship.cpp:1804-1808, 4021-4037`).
- The whirlpool `Auzu` (`daObjAuzu`) stands at (-205662, 0, 329245) on the same layers, parameters 0x971C.
  With the field widths in `d_a_obj_auzu.h:21-31` that is type 0, link point 151, save switch 0x1C, appear 0.
  Type 0 exists only with `ENDLESS_NIGHT` (`is_exist`, `d_a_obj_auzu.cpp:114-118`). With appear 0 it is full
  size while switch 0x1C is off and shrinks away once the wall breaks (`:84-91`, `:214-219`).
- Getting too close pulls the boat under: `daShip_c::procWhirlDown` sets 0x1940 and changes scene to the
  whirlpool's link point, `sea` 44 point 151, a boat point next to it (`d_a_ship.cpp:2887-2893`). 0x1940 only
  changes the King of Red Lions' hint to 0xD61, "break the stone slab" (`:500-501`). It is off in every catalog
  save, so it's an optional flag of this step, not a step.

## Into the cave and the pearl

- `ajav_uzu`, in the sea stage's event list, ends with a DIRECTOR `NEXT` cut: Stage `Pjavdou`, RoomNo 0,
  StartCode 200, Layer 8, Mode 1.
- `Pjavdou` point 200 (parameters 0x00FF0000) starts the stage's event 0, `getperl_jab`. Its `EVNT` record has
  no spawn switch (0xFF), so it would play on every arrival at point 200; only `ajav_uzu` leads there.
- Jabun (`Jb1`) is placed only in `Pjavdou` room 0's `ACT8`, so he's only there on that cutscene's layer 8.
  Outset's own exit to the cave (`sea` 44 exit 7 → `Pjavdou` point 0) loads its normal layers, without him.
- `getperl_jab`: a `PACKAGE` `PLAY` cut with `FileName` `getperl_jab.stb` and `EventFlag` 14624 = 0x3920 (the
  decomp's note agrees, `d_save_event_flag.inc:435`); a `DIRECTOR` `NEXT` cut to `sea` 44 point 9 (start mode 5,
  at the cave mouth, (-205651, -102, 324657)).
- The pearl: `getperl_jab.stb` is in `res/Object/Demo18.arc`. Its demo item payload is 5: the block
  `000c0081 00000004 00000005` followed by `31 05` at 0x1634. The same block holds `31 03` in
  `getperl_komori.stb` (`Demo11`, Din's Pearl) and `31 04` in `getperl_deku.stb` (`Demo15`, Farore's Pearl).
  `d_a_demo00`'s `l_itemNo` table (`d_a_demo00.cpp:715-735`) has payloads 3, 4 and 5 as Din's, Farore's and
  Nayru's Pearls.
- The developers' stage select lists the scene in its cutscene group: "(18) Get the sacred pearl from Jabun",
  `Pjavdou` point 200, layer 8 (bench folder `stage-select-list-ja.tsv`, group 32 entry 17).

## The end of the Endless Night

- The night ends with the pearl, not a flag: `dKy_checkEventNightStop` is `ENDLESS_NIGHT` and not the Nayru
  symbol (`d_kankyo.cpp:3162-3167`). `ENDLESS_NIGHT` stays on (catalog 18 to 41).
- Other readers switch the same way: Windfall's people (`d_a_npc_people.cpp:5014`, `6980` and on), the bomb shop
  counter (`d_a_obj_pbco.cpp:36-48`).
- 0x3920 is read later by the sea chart (`d_menu_fmap.cpp:922`), the Tingle Tuner (`d_a_agb.cpp:1235`), Lenzo
  (`d_a_npc_photo.cpp:2202`) and the music (`JAIZelBasic.cpp:1771`).
- The King of Red Lions then gives hint 0xD5A, "the curse is broken; morning will come" (`d_a_ship.cpp:359-360,
  497-498`). Reading 0xD5B sets 0x2F20 (`:656-657`): the next arc's start.

## Hazard for crafted saves

Switch 0x1C on without Nayru's Pearl leaves the wall open with no way to the pearl: only `ajav_uzu` starts
`Pjavdou`'s layer 8, where Jabun is. The Endless Night would never end.

## Catalog (`arcs.position` on these two steps)

| Entries | Position |
|---|---|
| 01-17 | not started (17 has the bombs) |
| 18, 19, 20 and later, 41 | `jabun_pearl` |

No catalog save comes out mixed.

## Not this part

Other changes between catalog 17 and 18: 0x3F80 (the King's "look for Jabun's cave" talk, message 0x1688,
`d_a_ship.cpp:665-666`; also set on boarding after 0x3E10, `d_a_player_main.cpp:12464-12467`: part B, rung 9);
0x2A20 Grandma healed with the Elixir Soup; 0x3010 the wallet upgrade on Outset; 0x3008 the Bomb Bag upgrade at
Eastern Fairy Island; the letter registers 0x7A03 and 0x9D03; 0x1410, 0x1440 and 0x2F20 (the next arc, placing
the pearls).
