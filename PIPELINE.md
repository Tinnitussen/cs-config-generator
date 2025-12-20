# Command Processing Pipeline

The Blazor app ships with generated command data under `CSConfigGenerator/wwwroot/data/`. This document explains how to regenerate that data using the Python pipeline in `CommandPipeline/`.

## What it produces

- **Output JSON (checked into repo)**: `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`
- **Loaded by the app via**: `CSConfigGenerator/wwwroot/data/manifest.json`

The JSON format is documented in `SCHEMA.md`.

## Prerequisites

- **Python**: 3.8+

## Quick start

1. In CS2, create a snapshot with `dump_commands`.
2. Put the snapshot into `CommandPipeline/data/` with a filename matching `all_commands-*.txt` (recommended: `all_commands-YYYY-MM-DD.txt`).
3. Run the orchestrator:

```bash
python CommandPipeline/pipeline.py
```

Non-interactive mode (auto-picks newest snapshot):

```bash
python CommandPipeline/pipeline.py --non-interactive
```

## What the orchestrator does

`CommandPipeline/pipeline.py` runs these steps:

- **Step 1**: Parse snapshot → `CommandPipeline/data/commands.json`
- **Step 2**: Initial type classification (`bool`, `float`, `string`, `command`, `bitmask`, `unknown`, …)
- **Step 3**: Numeric refinement using configs (player + server)
- **Step 3.5**: Apply type improvements (manual overrides + vector heuristics)
- **Step 4**: Copy `commands.json` → `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`

## Key inputs (besides the snapshot)

- **Manual overrides (highest priority)**: `CommandPipeline/data/manual_type_overrides.json`
- **Config sources for numeric refinement**:
  - `CommandPipeline/data/pro-player-configs/unzipped-configs/`
  - `CommandPipeline/data/server-configs/`

## Classification strategy

Types are determined through a layered approach:

1. **Deterministic heuristics** (automatic):
   - `null` default → `command`
   - `true`/`false` default → `bool`
   - "bitmask" in description → `bitmask`
   - Float literal (contains `.`) → `float`
   - Space-separated triple → `vector3`
   - Space-separated pair → `vector2`

2. **Numeric detection** (from config files):
   - Analyzes pro player and server configs
   - Refines `unknown` types to `float` or `int` based on usage patterns

3. **Manual overrides** (human-verified):
   - Add entries to `manual_type_overrides.json`
   - Use the interactive classification tool: `python CommandPipeline/scripts/classify_interactive.py`

## Common tasks

### Classify unknown commands interactively

```bash
python CommandPipeline/scripts/classify_interactive.py
```

### Run pipeline tests

```bash
python -m unittest discover -s CommandPipeline/tests
```

## Troubleshooting

- **No snapshots found**
  - Ensure there is at least one `CommandPipeline/data/all_commands-*.txt`.
- **Wrong type**
  - Add an entry to `CommandPipeline/data/manual_type_overrides.json`, then re-run the pipeline.

## Related

- **[SCHEMA.md](SCHEMA.md)**: JSON format produced/consumed

