# Which story flags matter

Working notes for the TODO item "Which story flags are required". The goal is a defensible rule
for story-progress presets: which of the 487 story flags must follow the preset, and which are
side content that stays as the player has it.

## Sources

- **zeldaret/tww decomp** (CC0), commit `bdde145`: every place the code reads (`isEventBit`) or
  writes (`onEventBit`, `offEventBit`, `revEventBit`) a story flag by name.
- **Wind Waker Randomizer** (MIT), commit `9775811`: `init_save_with_tweaks` in
  `asm/patches/custom_funcs.asm`, which turns flags on for a new file so that the game can be
  played out of order, and `asm/patches/make_game_nonlinear.asm`, which changes game code where
  setting flags is not enough.
- **The catalog's flag timeline** (`flag-timeline.txt`): when each flag turned on in a real
  playthrough.

`flag_evidence.py` collects all three into `story-flag-evidence.csv`, one row per flag. It also
has the editor's current guess (`wwgui.mandatory_flag`) for comparison. ZeldaSpeedRuns
descriptions are left out because that sheet must not be committed.

## Findings so far

### Counts

| | Played (turned on in the timeline) | Not played |
|---|---|---|
| Read by game code | 170 | 134 |
| Not read by game code | 49 | 134 |

Reads by the GBA/Tingle Tuner actors (`d_a_agb`, `d_a_agbsw0`) don't count here, since they only
affect the Tingle Tuner. A flag that isn't read by code can still be read by event or message
data on the disc, so "not read" means "not read by named code", not "unused".

### Flags that change the world (decomp)

- **Stage layers**, from `dComIfG_play_c::getLayerNo`, which decides which actors exist on a whole
  island or stage. There are 12 flags:
  - Outset: 0x0520, else 0x0E20, else 0x0101.
  - Windfall: 0x2D01.
  - Forsaken Fortress: 0x1820.
  - Forest of Fairies (`A_mori`): `MET_KORL` 0x0F80.
  - `Asoko`: 0x0520.
  - Hyrule, `Hyroom`, `kenroom`: 0x3280, 0x2C01, 0x3B40, `COLORS_IN_HYRULE`, and the Triforce
    count.
  - `M2tower`: 0x2D01.
  - `GanonK`: 0x3B02.
  - `GTower`: 0x4002.
- **Restart place**, from `dComIfGs_setGameStartStage`. The first flag that is set wins:
  `RODE_KORL` 0x2A08 (then it depends on the current area), `MET_KORL` 0x0F80 (Windfall 128),
  0x0801 (`MajyuE` 0), 0x0808 (`MajyuE` 18), 0x2401 (`A_umikz` 204), otherwise Outset. The
  editor already has this as `START_RULES` in `tools/wwcat.py`.
- **Island landings**, from `dComIfGs_checkSeaLandingEvent`. Saving on these islands only
  restarts there once their arrival flag is set:

  | Island | Flag |
  |---|---|
  | Forsaken Fortress | 0x3040 |
  | Gale Isle | 0x2E02 |
  | Dragon Roost Island | 0x0902 |
  | Greatfish Isle | `ENDLESS_NIGHT` |
  | Forest Haven | 0x0A20 |
  | Headstone Island | 0x2E04 |

  The editor doesn't model this yet.

### Much of the world follows items, not flags (Randomizer)

`make_game_nonlinear.asm` patches code that checks inventory rather than flags:

- The King of Red Lions' sailing bounds check the pearls and the Master Sword.
- Medli and Makar leave once you have the Master Sword at half or full power.
- The withered trees and the Koroks wait for Farore's Pearl.
- The Komali, lava and mailbox changes follow Din's Pearl.
- The bomb shop prices follow Nayru's Pearl.
- The Earth and Wind Temple tablets check the songs.

Story-progress mode already sets items, pearls, songs and sword level from the preset, which
covers these.

### The Randomizer's new-file flags

45 save flags are turned on unconditionally, plus a few only with an option: swordless sets
0x2C02 and 0x3B08, 8 starting shards sets 0x3D04, and skip rematch bosses sets
0x3901/0x3902/0x3904/0x3A80. These flags are safe to have on early, but only together with the
Randomizer's code patches, so they are evidence of "event already seen", not proof that vanilla
handles them out of order.

The Randomizer also sets a bit 0x0310, but in the temporary bits (`dSv_info_c::mTmp`,
`0x803C5D60`), not the saved ones (`0x803C522C`). The addresses come from `include/d/d_save.h`:
the save starts at `0x803C4C08`, `mEvent` is at +0x624 and `mTmp` at +0x1158. The Randomizer's
note ("Saw event where Grandma gives you the Hero's Clothes") therefore describes temporary bit
0x0310, while `tools/wwcat.py`'s `WWRANDO_NOTES` attaches it to save flag 0x0310. The Randomizer
isn't wrong here; our tool applied its note to the wrong set of bits.

It also sets stage switch bits (Outset, sea, Dragon Roost Cavern, Forbidden Woods, Tower of the
Gods, Earth Temple, Hyrule, Ganon's Tower) and each dungeon's "seen boss intro" bit. Those are
per-area memory (`dSv_memory_c`), separate from story flags. Presets have to carry them too.

### Where the current guess goes wrong

- Read by code, on in the playthrough, but guessed optional: 34 flags. Calling these "side
  content" from their descriptions is the same mistake the heuristic makes. Many are steps of a
  chain that later steps check. Mrs. Marie (`d_a_npc_ho`) reads first talk 0x1E01, hide and seek
  started 0x2201, hide and seek beaten 0x1340, Killer Bees talked to 0x1E04 and the Joy Pendant
  reward 0x1C08. Hide and seek leads to the talk about her birthday and her taste in jewelry, and
  the Joy Pendants can't be given for the Cabana Deed before that. Others are dungeon state that
  the word "first time" pushed out:
  - Tower of the Gods rainbow bridge: 0x0E01 and 0x0F40 (`d_a_lbridge`).
  - Tower of the Gods lasers: 0x1010 (`d_a_obj_bemos`).
  - Grappling Valoo's tail: 0x0420.
  - Medli's grapple bar text: 0x1280.
- Guessed required although not read by code and never on in the playthrough: 11 flags. Worth a
  look.

## Chains

Each chain lists its steps in order, with the flag, the code that sets it, and what the next step
checks. Source lines refer to the decomp commit above. "Msg" numbers are message IDs. Their text
is read locally from the disc's `res/Msg/bmgres.arc` and isn't committed.

### Mrs. Marie and the Killer Bees (Windfall) → Cabana Deed → Triforce Chart 2

Leads to a Triforce shard, so it is part of the main story: the Cabana Labyrinth's upper chest
holds Triforce Chart 2 in vanilla (Randomizer `logic/item_locations.txt`, "Private Oasis - Cabana
Labyrinth - Upper Floor Chest"; it also needs the Skull Hammer and Wind's Requiem).

| # | Step | Flag | Set by | Checked by |
|---|---|---|---|---|
| 1 | First talk with Mrs. Marie | 0x1E01 | `daNpc_Ho_c::getMsg` | the same (her greeting changes) |
| 2 | First talk with the Killer Bees | 0x1210 | `daNpc_Mk_c::getMsg` | the same |
| 3 | Mrs. Marie asks you to deal with the boys (choice in msg 0x2718) | 0x1380 | `daNpc_Ho_c::next_msgStatus` | `daNpc_Mk_c::getMsg` (the Bees' line changes) |
| 4 | Hide and seek started | 0x2201 | `daNpc_Mk_c::talk01` | `daNpc_Ho_c::next_msg_sub0` |
| 5 | Hide and seek won | 0x1340 | `daNpc_Mk_c::demoProc` | `daNpc_Ho_c::next_msg_sub0`, `daNpc_Mk_c::getMsg` |
| 6 | Mrs. Marie's reward (Purple Rupee) | 0x1F80 | `daNpc_Ho_c::next_msg_sub0`, needs 0x2201 and 0x1340 | `daNpc_Mk_c::visitTalkInit`, `visitSetEvent` |
| 7 | The Bees visit and talk about her birthday and jewelry (events `MK_TALK3`/`MK_TALK4`; content from playing it, message text not read yet) | 0x1E04 | `daNpc_Mk_c::visitTalkInit`, needs 0x1F80 and not 0x1E02 | `daNpc_Ho_c::wait01`: only with it does she accept a shown item (`SetOrder(HO_FLAG_00000004)`); without it, pulling out a Joy Pendant "does nothing here" (seen in game). `getMsg`: with it, showing any other item gets msg 0x2739 |
| 8 | Rolling into the Windfall tree that drops a Joy Pendant (meaning from ZeldaSpeedRuns, reworded) | 0x1E02 | `daTag_Mk_c::actionReady`, when an event the tag requested starts | `daNpc_Mk_c` visit functions: the Bees' visit (step 7) only happens while it is off |
| 9 | Joy Pendants given | register 0xC0FF (running total) | `daNpc_Ho_c::receivePendant(n)` adds n | rewards below |
| 10 | 21 given: Cabana Deed (ZeldaSpeedRuns and the Randomizer both say 21) | 0x1C08 | `daNpc_Ho_c::next_msgStatus`: msg 0x2742 takes 20 at once (`receivePendant(0x14)`), then msg 0x2743 gives the deed | `daNpc_Ho_c::getMsg` |
| 11 | 40 given: Hero's Charm | 0x1C04 | `daNpc_Ho_c::next_msgStatus` (register ≥ 0x28) | `daNpc_Ho_c::getMsg` |
| 12 | Cabana Deed shown at the cabana door | 0x2D80 | `daTag_Mk_c::getMsg` | `daKnob00` door, sea chart island name (`d_menu_fmap`), `dMsg2_Create` |

Notes:

- Step 8: the code doesn't say which of `daTag_Mk_c`'s events sets 0x1E02, so the sheet's meaning
  stands. What the code adds: the Bees' visit in step 7 requires 0x1E02 to be off, so the order
  of steps 7 and 8 matters. Worth a check in game: does bonking the tree before the visit skip
  the visit?
- Step 10: the 21 is consistent with the code if the first pendant was given earlier (the Red
  Rupee reward for one pendant in the Randomizer's list); the deed conversation itself takes 20.
- `daNpc_Mk_c::visitTalkInit` also has a second branch: talked to Lenzo (0x1208) without owning a
  Picto Box sets 0x1602. That's another chain (Lenzo).
- For presets: steps 1–12 move together. A preset past step 10 needs the Cabana Deed item and the
  register too, and a preset before step 7 must not have 0x1E04 or Mrs. Marie will take pendants
  too early.

### The main story spine: the King of Red Lions' hints (`daShip_c::setInitMessage`)

When you talk to the King of Red Lions, he gives a hint about where to go next. The function
checks story flags from latest to earliest and takes the first one that is set, so its order
*is* the story's order as the game sees it. Below it is listed earliest first. The meanings are
paraphrased from each hint's message, read from the disc locally; that text isn't committed.
Items and songs that the ladder also checks are shown in italics.

| # | Flag (or item) | Hint message | Stage of the story the hint implies |
|---|---|---|---|
| 1 | none / 0x0908 / `RODE_KORL` 0x2A08 | 0x5E0 / 0x5DF / 0xD5C | Found a sail, sailing lesson / climb aboard / follow the sea chart |
| 2 | 0x0902 (Dragon Roost arrival), 0x0A10, *Din's Pearl* | 0x5EA / 0x5EB / 0x5EC | Dragon Roost: ask the Rito about Valoo / monsters were Ganon's doing |
| 3 | 0x0A80, 0x1980 | 0x5EE, 0x5EF / 0xD5D | Pearl in hand; wait for the wind / go to the marked spot |
| 4 | 0x0A20 (Forest Haven arrival), 0x2B80, *Farore's Pearl* | 0x5F4 / 0x5F5 / 0x5F6 | Forest Haven: withered islands, see the Deku Tree / Ganon attacked here too |
| 5 | 0x0A08, 0x0A04, 0x2A02 | 0x5F8 / 0x5F9 / 0xD5E | Next destination marked / changing the wind / hurry to the mark |
| 6 | `ENDLESS_NIGHT` 0x0A02, 0x0A01, 0x2A01 | 0x607 / 0x608 / 0xD5F | Jabun has survived; go to Windfall and learn the pirates' plans |
| 7 | 0x1F04, 0x2110, *Bomb Bag* | 0x621 / 0x623 / 0x624 | See what the pirates are doing / the password / bombs ready, meet the pirates in the morning |
| 8 | 0x1F02 | 0xD60 | Sail home to Outset |
| 9 | 0x3E10, 0x3E01, 0x3F80 | 0x1687 / 0x1688 / 0x1689 | Outset: see your family / look for Jabun's cave / it's blocked by a stone door |
| 10 | 0x1940 | 0xD61 | Break the stone slab to get into the cave |
| 11 | *Nayru's Pearl* | 0xD5A | The curse is broken; morning will come |
| 12 | 0x2F20 | 0xD62 | Place one pearl at each marked spot |
| 13 | 0x1E40 (Tower of the Gods raised) | 0xD64 / 0xD63 | Climb the Tower of the Gods / in a dungeon: borrow the gods' power |
| 14 | 0x2D10 | 0xD65 | Hyrule: the power is in the castle |
| 15 | *Master Sword equipped* | 0xD66 | Preparations complete, come back to me |
| 16 | 0x3810 | 0xD67 | Head for the Forsaken Fortress to save your sister |
| 17 | 0x3040 (Forsaken Fortress landing) | 0xD68 | Your sister is at the top of the central tower |
| 18 | 0x3910, 0x3380 | 0xD7B / 0xD69 | Leave before Zelda is found / the temples can't be entered easily, gather information |
| 19 | *Earth God's Lyric or Wind God's Aria* | 0xD6A | Ganon has reached the sages; find the new sage |
| 20 | 0x1620 (Medli in dungeon mode) | 0xD6B | Guide her to the temple |
| 21 | 0x2E04 (Headstone landing) | 0xD6C | The Master Sword's power isn't full yet |
| 22 | 0x3A02, *Wind God's Aria* | 0xD6D / 0xD6E | The sage of the other temple is in danger / guide the new sage to the remaining temple |
| 23 | 0x1610 (Makar in dungeon mode) | 0xD6F | Guide this one to the temple |
| 24 | 0x2E02 (Gale Isle landing) | 0xD70 | The sword still hasn't regained its power |
| 25 | 0x4004, *8 Triforce shards* | 0xD71 / 0xD72 | Gather the eight shards / the Triforce is complete, go to the Tower of the Gods |
| 26 | 0x2D08 | 0xD73 / 0xD74 | The way to Hyrule is open / check on Zelda in the castle |
| 27 | 0x2C01 | 0xD75 | Zelda has been taken; the way is beyond the bridge |
| 28 | `BARRIER_BREAK` 0x2C02 | 0xD76 | Ganon's Tower |
| 29 | 0x3D02 | 0xD77 / 0xD78 | Inside: enter the light to return / outside: the world above is calm |

Before the ladder, 0x2110 without a Bomb Bag gives the password reminder (0x623).

Notes:

- Every flag here is a milestone of the main story. A preset at milestone *n* needs every
  milestone up to *n* on and every later one off. These flags are the spine for checking a
  preset and for building one.
- Some milestones are items, not flags (pearls, Master Sword, songs, 8 shards). Story-progress
  mode already copies those.
- `daShip_c::setNextMessage` sets some flags itself once a hint has been read: message 0x5E4
  sets 0x0908, 0x5EA sets 0x0A10, 0x5ED sets 0x0A80. The rest of the function isn't mapped yet.
- Checked against the playthrough: the timeline turns these flags on in ladder order, with no
  step out of sequence. 0x0A10, 0x2B80, 0x0A04 and 0x1940 never turned on, which suggests they
  are only set by talking to the King at that point and only change his hint. Not required,
  probably, pending a look at what sets them.
- The meanings in the last column come from the hints and are inferred. Each is still to be
  checked against the flag's other readers.

### Stage layers (`dComIfG_play_c::getLayerNo`)

A stage room's actors, scaled objects and chests come in up to 12 layers (`ACT0`–`ACTb`,
`SCO0`–`SCOb`, `TRE0`–`TREb`; `dStage_dt_c_roomLoader`). The base lists (`ACTR`, `SCOB`, `TRES`)
always load. Spawn points (`PLYR`) are not per-layer, so the editor's spawn check doesn't depend
on layers. `getLayerNo` picks the layer from story flags. Without a flag it uses the time of day:
layer 0 from 6:00 to 18:00, otherwise 1 (1 also during the Endless Night). An event can also
force a layer (`dComIfGp_getStartStageLayer`), which is how layers 6–b get used. The first
matching rule wins, so the checks are listed in the game's order. "Layer n|m" means n by day,
m by night.

Actor contents were read from the disc (`res/Stage/<stage>/Room<n>.arc`), and character names come
from comments in each actor's decomp source. Stage names are from the Randomizer's
`data/stage_names.txt`.

| Stage | Rule (in order) | Layer | What that layer has |
|---|---|---|---|
| Outset (`sea` room 44) | 0x0520 | 4\|5 | No pirates, Tetra or Helmaroc. Day: `Ah`, `Ym2`, `Yw1` (Sue-Belle), switch `SW_C00`, grass and flowers. Night adds `Ajav`, `Auzu`, `Puti`. |
| | else 0x0E20 | 2\|3 | Pirates and Tetra (`Zl1`) still there; Aryll (`Ls1`) gone. |
| | else 0x0101 | 9, day or night | Helmaroc (`Dk`), Aryll, Tetra, the pirates (`P1a`). |
| | none | 0\|1 | Prologue cast, Aryll included. |
| Windfall (`sea` room 11) | 0x2D01 | 4\|5 | 0\|1's cast with `Gk1` and `Kk1` added and `Pf1` gone. |
| | else `dKy_checkEventNightStop` (the Endless Night) | 2\|3 | Pirates; few townspeople. |
| | none | 0\|1 | Normal town. |
| Forsaken Fortress (`sea` room 1) | 0x1820 | 3 | No guards. `Akabe`, `Warpmj`, `Gaship2`. |
| | none | 1 | The fortress with its guards (`Bk`, searchlights, cannons). There's no day layer. |
| Outset Island Fairy Woods (`A_mori`) | `MET_KORL` 0x0F80 | 2\|3 | Moblins (`mo2`). |
| | none | 0\|1 | Tetra, a pirate and Bokoblins (`Bk`): the prologue rescue. |
| Pirate Ship Interior (`Asoko`) | 0x0520 | 2\|3 | No `P1c` and no rope-swing lifts; adds `Ospbox` ×35. |
| | none | 0\|1 | Rope game set-up with `P1c` and `P2b`. |
| Forsaken Fortress Tower, 2nd visit (`M2tower`) | 0x2D01 | 2\|3 | Helmaroc King boss (`Bdk`) and doors, by night only. |
| | none | 0\|1 | Night: Helmaroc, Aryll, Tetra, pirates. Day layer has nothing. |
| Hyrule Castle (`Hyrule`) | 8 Triforce shards | 4\|5 | Darknuts (`Tn`) and Moblins. |
| | else 0x3280 | 2\|3 | `Zl1` (Tetra/Zelda's actor). |
| Hyrule Castle Interior (`Hyroom`) | 8 shards and not 0x2C01 | 4\|5 | Nothing on these layers. |
| | else 0x3280 | 2\|3 | `Zl1` and an event tag. |
| | else 0x3B40 | 6\|7 | Nothing on these layers. |
| | none | 0\|1 | Darknuts and Moblins. |
| Master Sword Chamber (`kenroom`) | 0x2C01, or `COLORS_IN_HYRULE` 0x3802 without 0x3280 | 6\|7 | Only lights (`bonbori`). |
| | else 8 shards | 4\|5 | Darknuts, `p_zelda`, `Yswdr00`, `ALLdie`, an event tag. |
| | else `COLORS_IN_HYRULE` | 2\|3 | The King of Hyrule (`Hi1`) and `Zl1`. |
| | none | 0\|1 | Event tags (`LTag1`, `TagEv`, `TagHt2`). |
| Ganon's Tower Puppet Ganon (`GanonK`) | not 0x3B02 | 8 | Puppet Ganon (`Bgn`), Ganon's bed (`Gbed`), `p_zelda`. |
| | 0x3B02 | 0\|1 | Puppet Ganon (`Bgn`) and attention tags; no bed or `p_zelda`. |
| Ganon's Tower Rooftop (`GTower`) | not 0x4002 | 8 | Ganondorf (`Gnd`), `p_zelda`, `Akabe` ×9. |
| | 0x4002 | 0\|1 | Ganondorf, `p_zelda`, `Ycage00` (`d_a_obj_barrier`), `Xfuta`. |

What sets each one:

| Flag | Set by | First on in the playthrough |
|---|---|---|
| 0x0101 | `daTag_Event` demo start (`demoInitProc`) | 44 (prologue, Aryll taken) |
| 0x0E20 | `daTag_Event` demo start | 44 |
| 0x0520 | Forsaken Fortress hint tags (`TagHt2` type 5, flag from the disc's actor data) | 03 (go find a sail) |
| 0x0F80 | `dEvent_manager_c::exceptionProc` | 03 |
| 0x2D01 | `rescue.stb` (`M2tower`), per the decomp's note | 22 |
| 0x1820 | `daWarpdm20` creation | 23 |
| 0x3280 | `runaway_majuto.stb`, per the decomp's note | 22 |
| 0x3802 | event data | 20 |
| 0x3B40 | event data | 20 |
| 0x2C01 | the `kenroom` fire wall, `daObjFirewall_c::retire_act_proc` (compiled code; the decomp's is NonMatching) | 36 |
| 0x3B02 | `kugutu_ganon.stb` (`GanonK`) | 40 |
| 0x4002 | `g2before.stb` (`GTower`) | never (playthrough ended before it) |

The ZeldaSpeedRuns sheet's layer notes for 0x0101 (layer 9), 0x0E20 (layer 2) and 0x0520 (layer 4)
agree with `getLayerNo`.

What this means for presets:

- Each stage's rules check the latest flag first, so having *later* flags on as well is
  harmless. The risk is a later flag off while an earlier one is on. For example, a save past
  the prologue with 0x0101 on but 0x0E20 and 0x0520 off puts Outset back on layer 9, with Helmaroc,
  Aryll and the pirates, day or night. Whether that replays the kidnapping or breaks something is
  untested.
- These flags should follow the preset as a set, per stage, together with the Triforce count
  for Hyrule.
- Two layers depend on things that aren't flags: the time of day (0\|1, 2\|3 …) and the Triforce
  count.

Checked against the developers' stage select (2026-10-09; `/res/Menu/Menu1.dat`, read with
`wwedit.menu_entries`; English names from the BlueWake session's `stage-select-names-en.tsv` in the
bench folder). The menu labels layers by "day": day *n* is layer 2*n* by day and 2*n*+1 by night,
and layers 8 and up are cutscene set-ups. Every rule above agrees with its labels:

| Stage | Rules above | The menu's entries |
|---|---|---|
| Outset (`sea` 44) | none 0\|1, 0x0E20 2\|3, 0x0520 4\|5, 0x0101 9 | L0 Outset, L2 day 1, L4/L5 day 2/night 2; L9 is the cutscene entry "Aryll kidnapped" (point 203) |
| Windfall (`sea` 11) | none 0\|1, Endless Night 2\|3, 0x2D01 4\|5 | L0/L1 day 0/night 0, L3 pirates (the Endless Night is always night), L4/L5 day 2/night 2 |
| Master Sword Chamber (`kenroom`) | 0\|1, 2\|3, 4\|5, 6\|7 | day 0 to night 3, all eight |
| Hyrule (`Hyrule`, `Hyroom`) | 0\|1, 0x3280 2\|3, 8 shards 4\|5 | day 0, day 1, day 2 |
| Forsaken Fortress (`sea` 1) | 1, 0x1820 3 | L1 Fortress 2nd, L2 Fortress 3rd |
| `A_mori`, `Asoko`, `M2tower` | 0\|1, then 2\|3 | L0 and L3 / L2; `M2tower` L1 "cutscene", L3 "no cutscene" |

Stages without a rule (Forest Haven inside, Dragon Roost, the café bar, Mila's school) appear with
day and night layers only, as `getLayerNo`'s time-of-day default says. Outset's L6 and L7 are named
as load and room tests.

### The sages: Medli (Earth Temple) and Makar (Wind Temple)

Spine steps 19–25. Each sage follows the same pattern: learn the song, show the Wind Waker, play
the song to awaken them, sail with them aboard, an arrival scene at their island, break the song
stone, the temple, then a prayer after the boss that powers up the Master Sword. Stage names are
from the Randomizer's `data/stage_names.txt`; "first on" refers to the catalog saves.

**Medli → Earth Temple**

| # | Step | Flag or item | Set by | Checked by | First on |
|---|---|---|---|---|---|
| 1 | Medli talks to Link on Dragon Roost (before the Earth God's Lyric) | 0x1402 | `daNpc_Md_c::next_msgStatus` | `daNpc_Md_c` | 25 |
| 2 | Show her the Wind Waker | 0x1504 | `daNpc_Md_c::next_msgStatus` | `daNpc_Md_c::initialMsgSetEvent` | 25 |
| 3 | Awakened by the Earth God's Lyric: she rides the King of Red Lions | 0x1608 | `daNpc_Md_c::initialMsgSetEvent`, `initialEndEvent` | `daNpc_Md_c::create` (ship type), `daTag_Island` type 5 | 25 |
| 3 | …and is in "dungeon mode" (can be lifted and called) | 0x1620 | the same | `daNpc_Md_c`, `daShip_c`, `daPy_lk_c`, `daNpc_Bm1_c` | 25 |
| 4 | Headstone Island arrival scene | 0x2E04 | `daTag_Island::demoInitProc`, only when 0x1608 is on | `daNpc_Md_c::create` | 27 |
| 5 | Song stone at the Earth Temple entrance broken | 0x2920 | event data | `daNpc_Md_c::create` | 27 |
| 6 | Temple hints, her jail call, caught by a Floormaster | 0x3301–0x3320, 0x3304, 0x3404, 0x4180 | `daTag_Md_cb`, `daNpc_Md_c` | `daTag_Md_cb::checkCondition` | 27–31 |
| 7 | Jalhalla beaten, the Zora sage's prayer | 0x3A02 | `pray_zola.stb` (`M_DaiB`), per the decomp's note | `daShip_c` hint ladder | 32 |
| 8 | Master Sword at half power | item `MASTER_SWORD_2` (`isCollect(0, 2)`) | the prayer event | `daNpc_Md_c::create`, `daNpc_Cb1_c::create` | — |

Where Medli appears (`daNpc_Md_c::create`):

| Stage | Medli is there when |
|---|---|
| any stage, once the Master Sword is at half power | only `M_DaiB` (Jalhalla boss room) |
| `sea` (Dragon Roost) | not 0x2E04, and 0x1820, and Dragon Roost Cavern's boss beaten |
| Rito Aerie (`Atorizk`) | not 0x2E04, and the letter not yet delivered (`dNpc_chkLetterPassed`) |
| Dragon Roost Cavern Entrance (`Adanmae`) | not 0x2E04, and the letter delivered |
| Dragon Roost Cavern Moblin room (`M_Dra09`) | not 0x2E04, and not 0x1101 (Grappling Hook) |
| Earth Temple Entrance (`Edaichi`) | 0x2E04, and not 0x2920 |
| Earth Temple (`M_Dai`) | 0x2E04 and 0x2920 |
| aboard the ship | 0x1608, and not 0x2E04 |

**Makar → Wind Temple**

| # | Step | Flag or item | Set by | Checked by | First on |
|---|---|---|---|---|---|
| 1 | Talk to Makar (before the Wind God's Aria) | 0x1880 | `daNpc_Cb1_c::next_msgStatus` | `daNpc_Cb1_c::getMsg` | 32 |
| 2 | Show him the Wind Waker | 0x1840 | `daNpc_Cb1_c::next_msgStatus` | `daNpc_Cb1_c::evInitMsgSet`, `getMsg` | 32 |
| 3 | Awakened by the Wind God's Aria: he rides the King of Red Lions | 0x1604 | `daNpc_Cb1_c::evInitEnd` | `daNpc_Cb1_c::create`, `daTag_Island` type 6 | 32 |
| 3 | …and is in "dungeon mode" | 0x1610 | the same | `daNpc_Cb1_c`, `daShip_c`, `d_a_mmusic` | 32 |
| 4 | Gale Isle arrival scene | 0x2E02 | `daTag_Island::demoInitProc`, only when 0x1604 is on | `daNpc_Cb1_c::create` | 32 |
| 5 | Song stone at the Wind Temple entrance broken | 0x2910 | event data | `daNpc_Cb1_c::create` | 32 |
| 6 | Temple hints, his jail call, caught by a Floormaster | 0x3480, 0x3440, 0x3408, 0x3410, 0x3420 | `daTag_Md_cb` | `daTag_Md_cb::checkCondition` | 32–34 |
| 7 | Molgera beaten, the Kokiri sage's prayer | 0x4004 | `pray_kokiri.stb` (`kazeB`), per the decomp's note | `daShip_c` hint ladder | 35 |
| 8 | Master Sword at full power | item `MASTER_SWORD_3` | the prayer event | `daNpc_Cb1_c::create` | — |

Where Makar appears (`daNpc_Cb1_c::create`). The first rule that matches decides, latest first:

| Rule | Makar appears as |
|---|---|
| full-power Master Sword | only the Molgera boss room type |
| else 0x2910 | only the Wind Temple type |
| else 0x2E02 | only the Wind Temple Entrance type |
| else 0x1610 | only on the `sea` stage, and only with 0x1604 (aboard) |
| else half-power Master Sword | only the `isTypeWaterFall` type (actor parameter 2; where it is placed isn't checked yet) |
| else 0x1820 | nowhere |
| else Farore's Pearl | only the Forest Haven type |
| else | nowhere |

**The partner's saved position** (`dSv_player_priest_c`, 16 bytes at card offset 0x1A4, already
in `tools/wwcat.py`): position, rotation, room and a flag (1 = Makar, 2 = Medli). It is written
by `daPy_npc_c` (`d_a_player_npc.cpp`): `setRestart` updates it when the partner is in a different
room from the saved one and not passing through a door, `unconditionalSetRestart` always, and the
spawn code when the partner is placed. When Medli is created in the Earth
Temple with flag 2, or Makar with flag 1, they restart from that saved position
(`dComIfGs_setRestartOption`), and the dungeon map shows them there (`d_menu_dmap.cpp`). The
Randomizer patches this because a stale position can put the partner in a later room or out of
bounds (`make_game_nonlinear.asm`). The editor never edits this record.

What this means for presets:

- The order inside each chain is enforced by the code: the arrival scene needs the sage aboard,
  and the sage's spawn rules follow 0x2E04/0x2920 and 0x2E02/0x2910. A preset must keep each
  chain's flags in order and match the Master Sword level to it (half power from step 8 of
  Medli's chain, full power from step 8 of Makar's).
- In vanilla the Earth Temple comes first: Makar only appears at the waterfall once the sword is
  at half power. The Randomizer removes these sword checks to allow either order.
- A preset inside either temple should copy the partner record along with the dungeon's state;
  a story-progress preset that leaves the player's record could place the partner from another
  save. The effects of a mismatched record are untested.

### Full cutscenes (`.stb`) and which lead into another

The disc's scripted cutscenes (`.stb`) are started from each stage's event list
(`event_list.dat` in `Stage.arc`; its layout is in the Randomizer's `wwlib/events.py`). The
code never names them. An event plays one with a `PACKAGE` actor's `PLAY` action, whose
properties give the file (`FileName`), the story flag it sets (`EventFlag`) and often where
to go when it ends (`Stage`, `StartCode`, `RoomNo`, `Layer`); a `DIRECTOR` `NEXT` action does
the same. 58 events play one, counting repeats on test and title stages (`VrTest`, `E3ROOP`,
`Ocean`, `sea_T`, `sea_E`).

`EventFlag` is set as the cutscene starts: `d_event_data.cpp` loads the `.stb` (from the stage's
demo archive or its own `Stage.arc`), creates the demo, then calls `dComIfGs_onEventBit` on it.
The flags read from the disc agree with all 24 of the decomp's "Set by …stb" notes in
`tools/wwcat.py` (three of those notes give the event's name, `departure_DEMO`, `FIND_SISTER`,
`MEETSHISHIOH`, where the disc has the file name).

How one cutscene leads into another: a spawn point's actor parameters hold an event number in
the top byte (`daPy_lk_c::getStartEvent`, `params >> 24`; 255 = none). When Link spawns there,
`dComIfGp_evmng_startDemo` starts that event from the stage's `EVNT` list. Each `EVNT` entry
is 0x18 bytes: its name starts at offset 1, and byte 0x13 is a stage switch that records that
a spawn has already triggered it (255 = none), so it plays once.

Checked against three sources, which agree:

- The decomp: `dStage_Event_dt_c` declares `u8 field_0x0` then `char mName[15]`, so `mName`
  is at offset 1. Its `/* 0x04 */` comment is a typo; the next field's `/* 0x10 */` (1 + 15)
  matches offset 1. `mSpawnSwitchNo` (0x13) "keeps track of whether this event has been
  triggered by a player spawn". `daPy_lk_c::getStartEvent` reads the spawn's event number as
  `params >> 24`.
- The Randomizer's `wwlib/dzx.py` (`EVNT`: name at `offset+1`, `event_played_by_spawn_switch`
  at 0x13) and `data/actor_parameters.txt` (`d_a_player_main`: `evnt_index` mask
  `0xFF000000`, `room_num` mask `0x3F`).
- The disc: reading at offset 1 gives whole event names (`getperl_komori`, `runaway_majuto`)
  that match the event lists; at 4 they lose their first three letters.

Cutscenes whose destination spawn starts a *different* cutscene:

| Cutscene (stage) | Sets | Goes to | Starts there |
|---|---|---|---|
| `master_sword.stb` (`kenroom`) | 0x2D04 | `Hyroom` spawn 248 | `rebirth_hyral.stb`, then on to `kenroom` spawn 249: `swing_sword.stb` (sets 0x3A04) |
| `attack_ganon.stb` (`M2ganon`) | 0x3910 | `ADMumi` spawn 244 | `runaway_majuto.stb` (sets 0x3280) |
| `find_sister.stb` (`Mjtower`) | 0x2580 | `sea` room 11 spawn 200 | `meetshishioh.stb` (sets 0x2E01) |
| `warp_in.stb` (`ADMumi`) | 0x2D10 | `Hyrule` spawn 200 | `warp_out.stb` |
| `howling.stb` (`Adanmae`) | — | `sea` room 13 spawn 210 | `getperl_komori.stb` |

Others end at a spawn whose event is the same cutscene (for example `dance_zola`,
`kugutu_ganon`, `g2before`, `bombshop`, `meet_deku`, `awake_zola`). Its spawn switch stops a
replay. `warphole.stb` and the two prayers (`pray_zola`, `pray_kokiri`) lead into short events
without an `.stb` (`WARP_ARRIVE`, `BOSS_WARPOUT`). The rest set no start event at their
destination.

For developer saves this suggests a way to start a cutscene on loading a save: restart at the
spawn point whose event is the cutscene, with that event's spawn switch and its story flag
off. Untested: whether a restart from a save starts the spawn's event the way arriving there
in play does.

### Cutscenes started by actors

Read 2026-10-07 (decomp, plus the disc's event lists, `EVNT`, `PLYR` and actor lists). Several
lines were spot-checked by hand (cited below); none of this is tested in game. "Walk-up" means
the actor orders the event when Link comes within a distance of it; "arrival" means it orders
it as soon as it is created, or a spawn point's event starts it. Temporary flags
(`dComIfGs_onTmpBit`) are not saved and are left out. `research/actor-events.md` lists about
35 more actors that start story or quest events and are not mapped yet.

**Prologue (Outset).** Aryll orders all three of her events from `daNpc_Ls1_c::eventOrder`
(`fopAcM_orderOtherEventId(mEventIDTbl[m850 - 3])`, `d_a_npc_ls1.cpp:1192-1201`).
`zelda_fly` is the telescope view of the Helmaroc King carrying Tetra, not the kidnapping.

| Step | Started by | Needs | Sets |
|---|---|---|---|
| Aryll wakes Link on the lookout | her type 3, which exists only while 0x2A80 is off (`decideType`, `d_a_npc_ls1.cpp:1443`); in `wait_action1` 0x2A80 off gives state 4 (`:2128`) | 0x2A80 off | — |
| `tale_1`, then `tale.stb` (Grandma, `LinkRM`) | walk-up to Grandma (`d_a_npc_ba1.cpp:1408-1418`); until then she waits in state 7 while 0x2A80 is off (`:1637`) | 0x2A80 off | a temporary flag; `LinkRM` spawn 200 starts `TALE_DEMO` (`tale.stb`), or spawn 202 `TALE_DEMO2` (`tale_2.stb`) in a second quest |
| Hero's clothes | `tale.stb` (Grandma's scene): its demo data passes index 1 to `d_a_demo00`'s flag table, which is 0x2A80 (`d_a_demo00.cpp:654`). `tale_2.stb` (second quest) passes the same index | — | 0x2A80 |
| Orca: sword lesson (`Ji1_EquipTalk`) | arrival: Orca starts it on creation while 0x0001 is on and 0x0108 off (`d_a_npc_ji1.cpp:4779-4781`); talking first time after 0x0001 also sets 0x0108 (msg 0x965) | 0x0001 | 0x0108 |
| Orca gives the Hero's Sword | his training: with 0x0001 on, 5 or more hits in a session (`field_0xD70 >= 5`) and 0x2F10 off (`:3009-3016`) | 0x0001 | 0x2F10; the sword (`createItem`, `dItemNo_SWORD_e`, `:1503`) |
| `omedeto` (birthday) | walk-up, 200 units (`wait_1`, `d_a_npc_ls1.cpp:1929-1933`) | 0x2A80 (her type 0), 0x0001 off, no Telescope | no flag |
| `get_telescope` | follows `omedeto` at once (`event_proc`, m850 = 5) | — | no flag; the Telescope item is the only record (who gives it is not in her code) |
| Postman through the telescope | `telescope_proc` (no event) | the Telescope | 0x0310 when message 0xBC2 closes (`:1831`) |
| `zelda_fly` | aiming above the postman (`telescope_proc`, m850 = 3) | 0x0310 in the same visit | 0x0001 at the end (`event_proc`, `onEventBit(1)`, `:1620`) |
| `look_tetra` (`A_mori`, the forest where Tetra fell) | not traced | | 0x0280 when the event starts (`dEvent_manager_c` exception events, `d_event_manager.cpp:601`) |
| `meet_tetra`, then the kidnapping | (see above: `daTag_Event`) | | 0x0101, 0x0E20 |
| `yuukaigo` (Tetra on Outset) | arrival (`daNpc_Zl1_c`, type 2) | 0x0E20 on, 0x2401 off (`init_ZL1_2`, `d_a_npc_zl1.cpp:312`), 0x0802 off | 0x0802 at the end (`:1844`) |

The Helmaroc King (`d_a_dk.cpp:252-268`) orders nothing. It shows from 0x0310, plays its part in
`zelda_fly` and hides once 0x0001 is on. 0x0310 also shows the pirates and their ship
(`d_a_npc_p1.cpp:1302`, `d_a_obj_pirateship.cpp:431,485`). Aryll's progress through the
telescope steps is kept in the actor, not the save: a save with 0x0310 on and 0x0001 off
probably restarts at the postman (untested). 0x2A80 means "wearing the Hero's clothes": Link wears his casual clothes while it is off, or in a
second quest (`d_a_player_main.cpp:12345`). That is why the Grandma scene comes before it and
`tale_2.stb` exists: the second-quest version, where Link keeps his own clothes (a reading of the
code, not checked against the `.stb`). It also means 0x2A80 cannot be set right after the
opening legend: Aryll's wake-up scene needs it off. Aryll's talk lines on the lookout (`getMsg_LS1_0`, `:1134-1145`;
meanings paraphrased from the disc's messages): with 0x0001 on, right after `zelda_fly`, she
says the girl fell into the forest (0xBC4/0xBC5, depending on whether Link has a sword); later,
without a sword, she says Link needs something to fight the bird off (0xBC7, so getting the sword
is a step of this arc); with 0x0280 on, the bird is searching for the girl and Link must hurry
(0xBC9). So 0x0280 marks that Link has reached the forest, and 0xBC9 is what she says if he goes
back to her before the kidnapping. Before 0x0001, with the Telescope owned, she explains how to
put it on X, Y or Z (0xBC0) and how to use it (0xBCB-0xBCD), matching the control the game
gives back after the gift.

Saves in the middle of the telescope steps: Aryll picks her state from the save each time she
loads (`wait_action1`, `:2124-2140`): 0x0001 on gives state 3 (done), else owning the Telescope
gives state 2 (the postman), else state 1 (the birthday). So the Telescope gift depends only on
not owning the Telescope, and the postman step needs the Telescope; neither depends on 0x0310.
The postman (`daNpc_Bm1_c`) doesn't read 0x0310. A save with 0x0310 on, the Telescope owned and
0x0001 off should replay the postman step from its start, with the Helmaroc King and the pirates
already showing. A soft lock isn't ruled out (untested), and one hazard is clear: 0x0001 on
without the Telescope puts Aryll in state 3, so nothing gives the Telescope any more. A slider
must set the Telescope with 0x0001.

**Flags and items given by cutscene data.** `d_a_demo00` reads two tables from a cutscene's demo
data: data ID 4 indexes a story-flag table, data ID 5 an item table (`d_a_demo00.cpp:651-730`). In
the `.stb` files the payload is the bytes `00 00 00 0N 31 xx` (ID N, a one-byte value xx). Read from
every `.stb` on the disc (48 files): flags: `tale.stb` and `tale_2.stb` 1 (0x2A80), `departure.stb`
5 (0x2401), `rescue.stb` 0x17 (0x2D01), `rebirth_hyral.stb` 0x31 (`COLORS_IN_HYRULE`);
`find_sister.stb` 7 and `seal.stb` 0x22 point at empty table entries. Items: `swing_sword.stb` 0
(Master Sword), `pray_zola.stb` 1 (Master Sword, half power), `getperl_komori.stb` 3 (Din's
Pearl), `getperl_deku.stb` 4 (Farore's), `getperl_jab.stb` 5 (Nayru's), `dragontale.stb` 6
(Delivery Bag), `get_shield.stb` 7 (Hero's Shield), `fairy.stb` and `fairy_flag_on.stb` 8
(magic arrows). The known ones (0x2401, 0x2D01, the shield) agree with the decomp's notes and the
timeline, which checks the reading.

**Prologue, part 2: the shield and the pirate ship.** After the kidnapping (0x0E20) and Tetra's
scene on Outset (`yuukaigo`, 0x0802):

| Step | Started by | Needs | Sets |
|---|---|---|---|
| The shield is missing (`LOOK_SHIELD`, `LinkRM` event 2) | walk-up to an event tag in Grandma's house (`TagEv` type 0xA, params 0x02FF110A); type 0xA only hunts once 0x0E20 is on (`d_a_tag_event.cpp:304-310`) | 0x0E20, room switch 0x11 off | room switch 0x11 as it starts; 0x3202 at the end (`demoEndProc`, `:148-149`) |
| Grandma gives the shield (`get_shield.stb`) | her type 1 (0x0520 off, 0x0001 on) with no shield (`checkCollect(1)`) and 0x3202 on: she moves, and once Link is on her floor the stage changes to `LinkRM` spawn 201, layer 9 (`d_a_npc_ba1.cpp:1548-1568`), whose spawn event is `get_shield` | 0x3202, no shield | the Hero's Shield (`get_shield.stb`, demo item table index 7) |
| Tetra lets Link aboard | talking to her (`daNpc_Zl1_c` type 2): without a shield she sends him to find one (0xCA1); with it, she asks if he's ready (0xC90); "yes" goes to `sea` spawn 0xCD, Outset, layer 10 (`d_a_npc_zl1.cpp:1008-1016, 2192-2206`) | the shield | 0x2908 if he says no (0xC91) |
| Departure (`departure_DEMO`, `sea`) | that spawn | | 0x2401 (`departure.stb`; also the demo's flag table, index 5); then `A_umikz` spawn 204 |
| On deck, Tetra sends Link to Niko | talking to her (`daNpc_Zl1_c` type 4) | | 0x0810 (msg 0x1005, `:2203`) |
| Niko's rope game | Niko (`daNpc_P2_c`) | | 0x0720 (`demo_jump`), 0x0710 (`demo_goal`) |
| Spoils Bag | the hold's chest (`DEFAULT_TREASURE`) | | the Spoils Bag |
| Tetra calls Link up (`P2B_ARRIVE_MAJYU`, `Asoko`) | Niko, once the chest event ends (`treasure_wait` waits on `endCheckOld`); message 0x102B, Tetra: "we've reached the Forsaken Fortress" | the Spoils Bag | **0x0808** (`daNpc_P2_c::demo_arrive`) |
| Talking to Niko afterwards | Niko (`getMsg`): his lessons must wait (0x1029) | 0x0808 | 0x0704 (`dLib_setFirstMsg`) |

The Niko rows come from the compiled game, not the decomp: `d_a_npc_p2` is NonMatching and its
functions are empty. Method: find `li r4, <flag>` in `rels/d_a_npc_p2.rel`, then resolve the next
`bl` through the module's relocations against the decomp's symbol tables
(`config/GZLE01/symbols.txt` and `rels/d_a_npc_p2/symbols.txt`). 0x0808 is set at `.text+0x2ADC`
(in `demo_arrive`, `onEventBit`); 0x0720 at `+0x1E94` (`demo_jump`); 0x0710 at `+0x28C0`
(`demo_goal`); 0x0704 at `+0x1660` (`getMsg`, `dLib_setFirstMsg`). From play (the owner's account): after Link shows the Spoils Bag, Tetra shouts from outside;
that is `P2B_ARRIVE_MAJYU`. In Niko's compiled code `treasure_wait` checks for an event's end and
`DEFAULT_TREASURE` is the only treasure event named in his module; the state change from there to
ordering `P2B_ARRIVE_MAJYU` (`eventOrder`, index from a variable) isn't read instruction by
instruction. 0x0704 (ZeldaSpeedRuns: after the Spoils Bag) is set on the first talk *after* 0x0808. With 0x0808 on,
saves restart at `MajyuE` spawn 18 (`d_com_inf_game.cpp:1308`), leaving the hold goes to the
fortress (`d_stage.cpp:2322-2328`), and the pirates say the ship has arrived (0x1017).

0x0520 (Aryll and the pirates leave Outset) is set by hint tags in the Forsaken Fortress
(`TagHt2` type 5, flag in the actor's Z angle, message 0x044D: `MajyuE` stage and `majroom` room 3;
`daTag_Hint_c::startProc`, `d_a_tag_hint.cpp:472-475`), found by scanning the disc's actor lists. It is clean-up: the player only sees it on the next visit to
Outset (`getLayerNo` uses Outset's layer 4 once it is on). In play that visit is during the Endless
Night (the owner's account), because the King of Red Lions keeps Link inside sailing limits.

**Sailing limits.** `daShip_c::checkOutRange` (`d_a_ship.cpp:990-1110`) tests the ship against the
paths that start at index `fopAcM_GetParam` (0: the only `Ship` actor, `sea` stage) in the `sea`
stage's own `RPAT`/`RPPN` (stage file, not a room; point offsets are relative to `RPPN`). Read
from the disc; squares are counted by whether their centre lies inside each path:

| Path | Applies until (the check skips it once this holds) | Area |
|---|---|---|
| 0 | 0x0902 on (Dragon Roost arrival) | keep-in: Windfall (11), Pawprint (12) and the western half of Dragon Roost's square (13): its edge is at x 199225, the square's centre at 200000, which is why a centre test leaves 13 out |
| 1 | Farore's Pearl owned | keep-in: 11, 12, Dragon Roost (13), Fire Mountain (20), Eastern Triangle (27), Bomb Island (34), Forest Haven (41) |
| 2 | Master Sword equipped | keep-out: the Forsaken Fortress square (1). Its points wind the other way from paths 0, 1 and 3 (signed area positive, theirs negative), and the check turns the ship back on one side of each edge |
| 3 | always applies | keep-in: the whole 7 x 7 sea, i.e. the edge of the world |

The King's line for paths 0-2 is 0x0609 (too soon to go this way; sail to the next destination),
for path 3 0x05DD (too dangerous to go further), and 0x060A during a minigame. So the pens are:
before 0x0902, Windfall to Dragon Roost ("pen zero"); from 0x0902 until Farore's Pearl, the
eastern corridor down to Forest Haven; after Farore's Pearl, the whole sea except the Forsaken
Fortress until the Master Sword. From play (the owner's account): the King won't set out from
Dragon Roost until Link has Din's Pearl and can change the wind, so in practice pen 1 starts
after Din's Pearl; that is a different check, not read yet. To test in game: a save just after
Forest Haven, sailing outside the eastern corridor.

So Outset (44) can't be reached until Farore's Pearl. From then on nothing in this check stops a
visit before Greatfish Isle and the Endless Night, though play doesn't lead there.

**First Forsaken Fortress visit (`MajyuE`).** Leaving the ship's hold (`Asoko` exit 0x3C) with
0x0808 on and 0x0520 off leads to `MajyuE` spawn 18 (`d_stage.cpp:2322-2328`), where the pirate
ship creates Tetra (`d_a_obj_pirateship.cpp:508-511`). 0x0808 is set by Niko (above).

| Step | Started by | Needs | Sets |
|---|---|---|---|
| `ooi` (Tetra calls you over) | walk-up (`demo_2`, `d_a_npc_zl1.cpp:2233-2240`) | 0x0801 off (`init_ZL1_3`), 0x0804 off | 0x0804 (`:1850`) |
| `majyuu_shinnyuu` (into the fortress) | walk-up (`demo_3`, `:2244-2257`) | 0x0804 | 0x0801 (`:1860`); the restart becomes `MajyuE` spawn 0 (`:1077`) |

With 0x0801 on, saves restart at `MajyuE` spawn 0 (`d_com_inf_game.cpp:1307`) and the sword is
taken away in the first fortress stage (`d_s_play.cpp:1370`). A slider moved back past this step
must undo both.

**Grandma (`LinkRM`).** Her `tale_2` table entry is never ordered by her code; the tale scenes are
spawn events.

| Step | Started by | Needs | Sets |
|---|---|---|---|
| `tale_1` | walk-up, 300 units (`wait_0`, `d_a_npc_ba1.cpp:1408-1418`) | her type 0: 0x0520 and 0x0001 off (`:150`) | a temporary flag only; goes to `LinkRM` spawn 200 (`tale.stb`), or 202 (`tale_2.stb`) when the clear count isn't 0 |
| Elixir Soup: `Use_Fairy`, `Ba1_Get_Itm`, `Ganbaru` | using a Fairy on her | 0x0520 on, 0x2A20 off | Soup in a bottle; at the end letter 0x9D03 and 0x2A20 GRANDMA_HEALED (`:1325-1331`) |

Both tale scenes end at `LinkRM` spawn 0 and set no story flag. Whether spawn switch 0x02 (shared
by both) stops a replay is not settled.

**Second Forsaken Fortress visit (`M2tower`).** Sea room 1 exit 16 leads to `M2tower` spawn 16,
whose event is `rescue` (no spawn switch). `rescue.stb` sets 0x2D01 and goes to `M2tower`
spawn 20, layer 3 (the Helmaroc King fight). `getLayerNo` uses layer 0 or 1 while 0x2D01 is off
(`d_com_inf_game.cpp:251`). The tide object only reacts to the event (`d_a_obj_tide.cpp:390-395`).
In the fight, `d_a_bdk.cpp` sets 0x3C01 (`:1583`); the exit leads to `M2ganon` spawn 0 and
`attack_ganon` (0x3910). Whether `rescue` replays on a later arrival is not settled.

**The Master Sword (`kenroom`).** The pedestal (`d_a_obj_vmsms.cpp`) orders nothing; it is not
created once 0x2D04 is on and deletes itself when `master_sword` starts (`:70-77`). A hint tag
(`TagHt2`) sets room switch 0x0E when its hint starts (`d_a_tag_hint.cpp:445-459`); then an event
tag at the pedestal (`TagEv`, params 0x000E0BFF) needs switch 0x0E and orders `master_sword`
when Link is within 200 units (`d_a_tag_event.cpp:66, 254-256`), setting switch 0x0B (also the
event's spawn switch). This adds two room-switch steps before the chain above (0x2D04, then
`rebirth_hyral`, then `swing_sword`, 0x3A04). Tetra's `nakaniwa` plays on arrival in Hyrule once
0x3280 is on, unless 0x3804 or 0x2D02 is on (`d_a_npc_zl1.cpp:348-353`); it sets 0x3804.

**Endgame (Hyrule, Ganon's Tower).**

| Step | Started by | Needs | Sets |
|---|---|---|---|
| 0x2C01 ("Zelda taken" in the King's hints) | the fire wall (`Yswdr00`, `daObjFirewall_c::retire_act_proc`, found in the compiled `d_a_obj_firewall.rel` at `.text+0x1BC8`; the decomp's version is NonMatching). It stands in `kenroom` on layers 4 and 5, used while all 8 shards are owned and 0x2C01 is off (`d_com_inf_game.cpp:237-248`). From play (the owner's account): Ganondorf has taken Zelda, two Darknuts drop in and a fire wall rings the arena; 0x2C01 is set when the fire wall goes, after the fight. The layer's Darknuts and `ALLdie` tag fit | 8 shards | 0x2C01 |
| `go_up_stairs2` (barrier cutscene) | arrival: the Hero statue orders it on creation (`d_a_obj_YLzou.cpp:127-136, 500-508`) | 8 shards, 0x2C01, 0x3980 off | 0x3980 at the end (`:466-472`) |
| `seal` (barrier broken) | a sword swing with the full-power Master Sword equipped, 8800+ units from the barrier (`d_a_obj_barrier.cpp:228-254`, USA build) | 0x3980 | 0x2C02 *before* the event; `seal.stb` sets 0x3B08 |
| Light warp appears (`APPEAR_WARP`) | a stage switch (`d_a_warpgn.cpp:189-194`) | 0x3D02 off | 0x3D02 at the end (`:405-409`) |
| `kugutu_ganon` (Puppet Ganon) | spawn event; `GanonK` layer 8 until 0x3B02 | | 0x3B02 |
| Puppet Ganon defeated | the fight (`d_a_bgn.cpp`) | | 0x3F10, then `GanonK` spawn 4 |
| `g2before` | spawn event; `GTower` layer 8 until 0x4002 (`d_com_inf_game.cpp:259-262`) | | 0x4002 |
| Ending, `endhr.stb` | after Ganondorf | | 0x3F40 |

With 0x2C02 on, the barrier is never created (`d_a_obj_barrier.cpp:496-508`), so moving back past
this step must clear it. The JPN build breaks the barrier without the sword check. From play (the owner's account): Link sneaks in and sees Zelda asleep in the middle of the arena
before Puppet Ganon, and `g2before` is either after Puppet Ganon or on reaching the roof. The
disc fits the roof: `kugutu_ganon` and `to_roof` are in `GanonK`'s event list, `g2before` and
`endhr` in `GTower`'s. Which spawn
points lead into `kugutu_ganon` and `g2before`, and where the light warp sits in the order, are
not settled (the order of 0x2C02 and 0x3D02 comes from the King's hints).

## Used in the editor

`wwedit.story_order_problems` turns the spine and the code-enforced rules above into warnings
(`STORY_MILESTONES`, `STORY_RULES`); the window shows them in *Review changes* and asks before
saving edits that cause new ones. Checked on 2026-10-07: every save from the catalog's
playthrough passes. The one save it flags is entry 49, crafted with 0x0908 cleared to replay the
King's sail speech.

## Next

"Main story or side content" is the wrong split. Flags belong to chains (quests, NPC
conversations, dungeons) in which later steps check earlier ones, and side chains can feed the
main story (the Triforce charts, for example). The plan:

1. **Map the chains.** For each code-read flag, read the code that checks it and record what it
   requires and what it unlocks. Group the flags by actor and by quest into chains with their
   order.
2. **Find what each chain gives**: an item, a gate in the main story, or nothing beyond itself.
3. **Rule for presets.** A chain is either copied whole from the preset or left whole as the
   player has it, never mixed, so no later step is on while an earlier one is off. Which chains
   follow the preset comes from step 2.
4. **Check the flags that code doesn't read**, the 49 that turned on in play, against the disc's
   event and message data.

Settled since: 0x0280 (`look_tetra`), 0x0808 (Niko), 0x0520 (fortress hint tags), 0x2C01 (the
`kenroom` fire wall). Flags with no setter in the decomp: search the compiled modules on the disc
(`li r4, <flag>`, then the call's relocation); `main.dol` is not covered by that search yet.

Done so far (2026-10-07): the spawn-point chains and the actor-started cutscenes above
(prologue, both Forsaken Fortress visits, Grandma, the Master Sword, the endgame). Next in
order: the main story's remaining gaps (which `.stb` sets 0x2A80, what starts `P2B_ARRIVE_MAJYU`;
the spawns into `kugutu_ganon` and `g2before`), then the chains that feed it (pearls, sages,
Triforce), then quest chains, working from `research/actor-events.md`.

Prologue arc (2026-10-09): 11 of its 12 unplaced flags are placed (`research/arcs/prologue.json`).
The forest's Bokoblins are a step (0x0004 drop; 0x0301, 0x0480 the first two defeated, any
Bokoblin, `d_a_bk` `fail`). On the ship, P1c's walk-up talk sets 0x0820. In the fortress,
0x0401 is a barrel picked up or a type-0 hint tag, and 0x0402 a rope (`d_a_himo3`, parameter 1;
no placed rope has that parameter, so how the game sets it differs from my reading). Quill's
first talk on Outset after the kidnapping is 0x1401. The Outset villagers' first talks
(0x0104 Joel & Zill, 0x0180 Sue-Belle, 0x0302 Rose, 0x0510 Sturgeon) are set in compiled code.
`relcalls.py` can't tell saved flags from temporary ones (both go through
`dSv_event_c::onEventBit`), so check `r3` before the call: game info + 0x624 is the saved flags,
+ 0x1158 the temporary ones. Still unplaced: 0x0201, set between the departure and waking on the
King of Red Lions, setter not found (see the arc). The prologue's order inside the ship ride and
the fortress isn't fixed by the code. Next for the arcs: the King of Red Lions / Windfall arc
(0x2580, 0x2E01, 0x0F80), using the restart table in `dComIfGs_setGameStartStage` and the
cutscene scene changes (`wwedit.disc_exits`).

King of Red Lions and Dragon Roost arc (2026-10-09): `research/arcs/korl_dragon_roost.json`, 22 steps
from `FIND_SISTER` in the fortress tower to the south wind after Din's Pearl, researched in three
parts in parallel. The evidence for each part is in `research/arcs/drafts/korl_a.md` (Windfall to the
first sail), `korl_b.md` (Dragon Roost Island) and `korl_c.md` (Dragon Roost Cavern to the pearl).
Every game-written catalog save lands on it in order. Unplaced: 0x0901 (a fishman diving away;
belongs to the fishmen and sea chart chain; since placed as `map_fish`, a window after Gohma).

Forest Haven arc (2026-10-09): `research/arcs/forest_haven.json`, 15 steps from the Forest Haven
arrival to setting off with Farore's Pearl, researched in three parts (`drafts/forest_a.md` Forest
Haven, `forest_b.md` the Forbidden Woods, `forest_c.md` Farore's Pearl and after). Every game-written
catalog save lands on it in order. The Song of Passing went to the previous arc as a window. Unplaced:
0x1E10 (Gillian's first night talk) and 0x2304 (Loot's first talk), first talks of Windfall chains.
Jabun arc (2026-10-09): `research/arcs/jabun.json`, 16 steps from the Endless Night at Greatfish Isle
to Nayru's Pearl (`drafts/jabun_a.md` the pirates, `jabun_b.md` the Bombs and Outset, `jabun_c.md`
Jabun's cave). Every game-written catalog save lands on it in order; nothing unplaced. The Endless
Night ends with Nayru's Pearl (`dKy_checkEventNightStop`), not by clearing 0x0A02. Next: the pearls
and the Tower of the Gods, from 0x2F20.

Your knowledge of the game is the check on each chain. Anything the code doesn't settle stays
marked as unknown.
