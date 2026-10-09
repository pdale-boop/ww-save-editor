# Story arcs

One JSON file per arc: a stretch of story as the player sees it, in order. These are the data
for the progress sliders planned in `TODO.md` (Features). `research/arcs.py` reads them and
reports where each save in a folder sits on each arc; run it after editing an arc.

Evidence for every step is in `research/story-flags.md`; the `evidence` lines here are short
pointers to it.
Arcs researched in parts keep each part's write-up in `drafts/` (`drafts/*.md`), next to the
part's step list it was joined from; `arcs.py` reads only the arcs in this folder, not `drafts/`.

## Format

```
{
  "id", "name", "summary", "notes",
  "status": "partial" | "mapped",      only "mapped" arcs get a slider
  "steps": [ step, ... ],              in story order
  "unplaced": {"flags": [...], "notes"}  set during the arc but not yet placed in a step
}
```

A step:

| Key | Meaning |
|---|---|
| `id`, `label` | short name; what the player sees |
| `sets.flags` | story flags (hex strings) the step turns on; checked |
| `sets.optional_flags` | flags only an optional talk sets; set with the step, not checked |
| `sets.items` | items the step gives, by `wwedit` name (`ITEMS_GIVEN`, `SWORDS`, `SHIELDS`, ...); checked |
| `sets.songs` | songs by name (`wwedit.SONG_NAMES`); checked |
| `sets.pearls` | pearls by name (`wwedit.PEARL_NAMES`); checked |
| `sets.dungeon_items` | `{"area", "items"}`: the area's dungeon-item bits (`dSv_memBit_c::mDungeonItem`, area block + 0x21): `MAP`, `COMPASS`, `BOSS_KEY`, `STAGE_BOSS_ENEMY` (boss beaten), `STAGE_LIFE` (heart container taken), `STAGE_BOSS_DEMO` (boss intro seen); checked |
| `sets.switches` | saved stage switches: `{"area", "switch", "why"}`. `area` is the stage's save area (`STAG`, `dStage_stagInfo_GetSaveTbl`); switches 0x00-0x7F are saved at area block + 0x04 (`dSv_memBit_c::mSwitch`). Spawn switches stop a scene replaying, so moving forward sets them and moving back clears them |
| `restart` | where the game would put the restart on saving at this step (`dComIfGs_setGameStartStage`, `l_checkData`) |
| `window` | `{"after", "by"}` (step ids, both optional: no `after` when it can also happen before the arc, no `by` when nothing later needs it): a step the player can do any time in that stretch. It is left out of the order and checked against it: not started before `after` is done, done once `by` is |
| `requires` | other steps (`arc:step`) that must be done first |
| `evidence` | decomp lines, disc data, compiled code |
| `basis` | `code`, `disc`, `compiled` (read from the game's compiled modules), `play` (the owner's account), or a mix |
| `seen`, `notes`, `warn` | what the player notices; open questions; hazards for crafted saves |

A save is at step n when steps 1..n are done and nothing in a later step is; anything else is
"mixed", and the checker says which later steps have started and what the first gap lacks.
