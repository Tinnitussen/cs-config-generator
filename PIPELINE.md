# Command Processing Pipeline

This document describes the Python-based command processing pipeline that transforms raw Counter-Strike 2 console data into structured JSON schema files used by the CS2 Config Generator application.

## Overview

The Command Pipeline is a standalone Python project that processes console command snapshots from Counter-Strike 2 and produces structured JSON data files. It serves as the data generation layer for the main Blazor application.

### Purpose

- Parse raw console command dumps from CS2
- Classify command types (bool, float, string, enum, etc.)
- Refine numeric type detection using real-world config files
- Generate standardized JSON schema files for UI consumption

### Key Features

- **Interactive workflow**: Review each processing step before continuing
- **Rule-based classification**: Extensible rules system for type detection
- **Error recovery**: Stops on failures with clear error messages
- **Non-interactive mode**: Supports automation via `--non-interactive` flag
- **Visual feedback**: Colored terminal output for easy monitoring

## Quick Start

### Prerequisites

- Python 3.8 or higher
- No external dependencies required (uses Python standard library only)

### Running the Pipeline

1. **Obtain a command snapshot** from Counter-Strike 2 (use the `dump_commands` console command)
2. **Place the file** in `CommandPipeline/data/` with the naming pattern `all_commands-YYYY-MM-DD.txt`
3. **Run the pipeline**:

```bash
cd CommandPipeline/
python pipeline.py
```

4. **Follow the interactive prompts** to complete all processing steps
5. **Review the output** at `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`

### Non-Interactive Mode

For automated workflows or CI/CD:

```bash
python pipeline.py --non-interactive
```

This will automatically process the newest snapshot file without waiting for user input.

## Pipeline Architecture

### Directory Structure

```
CommandPipeline/
├── pipeline.py                              # Main orchestrator (START HERE)
├── rules/                                   # Type classification logic
│   ├── type_classification_rules.py        # Command type detection rules
│   ├── numeric_detection_rules.py          # Numeric type refinement rules
│   └── parsing_validation_rules.json       # Command parsing validation rules
├── scripts/                                 # Processing scripts
│   ├── parse_commands.py                   # Step 1: Parse raw snapshot
│   ├── command_classification.py           # Step 2: Classify command types
│   ├── numeric_detection.py                # Step 3: Refine numeric types
│   └── create_all_commands.py              # Step 4: Generate UI data file
├── utils/                                   # Shared utilities
│   └── paths.py                            # Centralized path management
└── data/                                    # Data files
    ├── all_commands-*.txt                  # Input: CS2 command snapshots
    ├── commands.json                       # Working file: processed commands
    ├── pro-player-configs/                 # Config files for numeric detection
    └── server-configs/                     # Additional configs for detection
```

### Data Flow

```
┌─────────────────────────────────────┐
│ all_commands-YYYY-MM-DD.txt         │  Raw CS2 console dump
│ (Input: CS2 snapshot)               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Step 1: parse_commands.py           │  Extract and structure commands
│                                      │  - Parse command name, description
│ Output: commands.json                │  - Extract default values & flags
│  {                                   │  - Create consoleData objects
│    "command": "...",                 │
│    "consoleData": {...}              │
│  }                                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Step 2: command_classification.py   │  Classify command types
│                                      │  - Apply type classification rules
│ Output: commands.json + uiData       │  - Determine bool/string/float/etc.
│  {                                   │  - Mark numerics as 'unknown' or 'float'
│    "command": "...",                 │
│    "consoleData": {...},             │
│    "uiData": {                       │
│      "type": "...",                  │
│      "label": "..."                  │
│    }                                 │
│  }                                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Step 3: numeric_detection.py        │  Refine numeric types
│                                      │  - Analyze pro player configs
│ Output: commands.json (refined)      │  - Check for decimal values
│  "type": "unknown" → "int"           │  - Convert 'unknown' to 'int'
│  "type": "unknown" → "float"         │    or 'float' based on usage
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Step 4: create_all_commands.py      │  Copy to UI location
│                                      │
│ Output:                              │
│ CSConfigGenerator/wwwroot/data/     │
│   commandschema/all_commands.json   │
└─────────────────────────────────────┘
```

## Type Classification System

The pipeline uses a rule-based system to automatically classify commands into types. Rules are defined in separate modules for maintainability.

### Classification Rules

Rules are applied in order. The first matching rule determines the command type.

#### Rule 1: Command Type

**File**: `rules/type_classification_rules.py` → `rule_command()`

**Condition**: `defaultValue` is `null`

**Result**: Type = `"command"`

Commands with no default value are executable actions (e.g., `quit`, `clear`).

#### Rule 2: Boolean Type

**File**: `rules/type_classification_rules.py` → `rule_bool()`

**Condition**: `defaultValue` is `"true"` or `"false"` (case-insensitive)

**Result**: Type = `"bool"`, defaultValue = `true` or `false` (boolean)

#### Rule 3: Bitmask Type

**File**: `rules/type_classification_rules.py` → `rule_bitmask()`

**Condition**: Description contains the word `"bitmask"`

**Result**: Type = `"bitmask"`, defaultValue = integer representation

Bitmask commands allow multiple flags to be combined (e.g., `sv_tags`).

#### Rule 4: Numeric Type

**File**: `rules/type_classification_rules.py` → `rule_numeric()`

**Condition**: `defaultValue` is a numeric string

**Result**:
- If value contains `.` → Type = `"float"`, defaultValue = float
- Otherwise → Type = `"unknown"`, defaultValue = integer

The `"unknown"` type is later refined to `"int"` or `"float"` by Step 3.

#### Rule 5: String Type

**File**: `rules/type_classification_rules.py` → `rule_string()`

**Condition**: `defaultValue` is any non-null, non-numeric value

**Result**: Type = `"string"`, defaultValue = string

This is the fallback rule for any remaining commands.

### Numeric Type Detection

Commands initially classified as `"unknown"` are analyzed by the numeric detection script.

**File**: `scripts/numeric_detection.py`

**Process**:
1. Scans pro player and server config files
2. Looks for actual usage of each command
3. Checks if any usage contains decimal points
4. If decimal found → convert to `"float"`
5. If no decimal found → convert to `"int"`

**Config Sources**:
- `data/pro-player-configs/` - Professional player configurations
- `data/server-configs/` - Community server configurations

This approach ensures type classification matches real-world usage.

## Adding New Classification Rules

To add a new command type or modify classification logic:

1. **Edit** `rules/type_classification_rules.py`
2. **Add your rule function**:

```python
def rule_my_new_type(cmd):
    """Rule description here."""
    console_default = cmd['consoleData']['defaultValue']

    # Your detection logic
    if some_condition:
        return 'my_new_type', processed_default_value

    return None
```

3. **Add to the rules list** in order of priority:

```python
CLASSIFICATION_RULES = [
    rule_command,
    rule_bool,
    rule_bitmask,
    rule_my_new_type,  # Add your rule
    rule_numeric,
    rule_string,
]
```

4. **Test** by running the pipeline on a snapshot file

## Output Schema

The pipeline generates JSON files conforming to the schema documented in `SCHEMA.md`. Each command has this structure:

```json
{
  "command": "cl_crosshairsize",
  "consoleData": {
    "sourcedAt": "2025-01-30T05:49:01Z",
    "defaultValue": "5",
    "flags": [],
    "description": "Size of the crosshair"
  },
  "uiData": {
    "label": "Crosshair Size",
    "helperText": "Size of the crosshair",
    "type": "float",
    "defaultValue": 5.0,
    "range": {
      "minValue": 0.5,
      "maxValue": 10.0,
      "step": 0.5
    },
    "requiresCheats": false
  }
}
```

See `SCHEMA.md` for complete schema documentation.

## Troubleshooting

### No snapshot files found

**Error**: `No command snapshot files found in CommandPipeline/data/`

**Solution**: Ensure your snapshot file matches the pattern `all_commands-YYYY-MM-DD.txt`

### Parsing errors

**Error**: Commands fail validation during Step 1

**Solution**:
1. Check `rules/parsing_validation_rules.json` for validation rules
2. Verify your snapshot file format matches CS2's `dump_commands` output
3. Look for malformed lines in the snapshot file

### Missing config files

**Warning**: `No config files found for numeric detection`

**Impact**: All `"unknown"` types will default to `"int"`

**Solution**:
1. Add config files to `data/pro-player-configs/` or `data/server-configs/`
2. Or manually edit `commands.json` after Step 2

### Type misclassification

**Issue**: A command gets the wrong type

**Solution**:
1. Review classification rules in `rules/type_classification_rules.py`
2. Adjust rule order or conditions
3. Add a specific rule for problematic commands
4. Rerun the pipeline

## Integration with Main Application

The pipeline outputs data consumed by the Blazor application:

**Pipeline Output**: `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`

**Consumed By**: `CSConfigGenerator/Services/SchemaService.cs`

The SchemaService loads the JSON at runtime and provides command data to the UI components.

## Best Practices

1. **Keep rules simple**: Each rule should have a single, clear purpose
2. **Test rule changes**: Run the pipeline on a full snapshot after modifying rules
3. **Document new types**: If adding types, update `SCHEMA.md` with the new type specification
4. **Version snapshots**: Use the date format in filenames to track data versions
5. **Review pipeline output**: Always check `all_commands.json` after processing
6. **Commit data files**: Check in the generated JSON so others can build without running the pipeline

## Related Documentation

- **SCHEMA.md**: Complete JSON schema specification for command data
- **README.md**: Main application documentation and setup
- **PROPOSAL.md**: Technical design decisions for the data structure

## Future Enhancements

Potential improvements to the pipeline:

- [ ] Automatic range detection for numeric types
- [ ] Enum option extraction from descriptions
- [ ] Multi-language description support
- [ ] Diff generation between snapshot versions
- [ ] Validation against previous schema versions
- [ ] Web scraping integration for additional metadata

