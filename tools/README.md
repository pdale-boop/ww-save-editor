# Research tools

Command-line tools used while working out the save format. They read paths from `../config.py`
(override them in `../config.json`). All of them are interactive: run them with no arguments.

- `wwcat.py` — browse BlueWake save states (`states` setting), open them in a BlueWake build from
  your checkout, catalog them as saves, check the extraction against saves the game made, and show
  a story-flag timeline across the catalog.
- `craft.py` — make a test save from a catalog entry and inject it into a card.
- `make_presets.py` — copy catalog entries into the presets folder with player-facing names.
- `vanilla_chart.py` — copy a catalog entry with its sea chart reset to a new file's.
