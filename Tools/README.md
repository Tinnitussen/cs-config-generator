# Tools Directory Documentation

This directory contains a Python-based pipeline for parsing and processing Counter-Strike 2 console commands. These tools are responsible for maintaining the JSON schema files that power the config generator's UI.

## Quick Start - Processing Pipeline

To process a new command snapshot from Counter-Strike 2:

1.  Place your `all_commands-YYYY-DD-MM.txt` file in `Tools/data/`
2.  Run the pipeline: `python Tools/pipeline.py`
3.  Follow the interactive prompts to complete all processing steps

The pipeline will guide you through:
- **Parsing** - Extract commands from the snapshot file
- **Classification** - Determine command types (bool, float, string, etc.)
- **Categorization** - Split commands into player/server/shared groups
- **Subcategorization** - Organize commands into UI sections

## Directory Structure

```
Tools/
├── pipeline.py              # Main pipeline runner (entry point)
├── src/                     # Source code for the pipeline and related logic
│   ├── __init__.py
│   ├── stages/              # Each major pipeline step is a "stage"
│   │   ├── __init__.py
│   │   ├── 1_parse.py
│   │   ├── 2_classify_types.py
│   │   ├── 3_categorize.py
│   │   └── 4_subcategorize.py
│   ├── rules/               # Rules are used by the stages
│   │   ├── __init__.py
│   │   ├── classification_rules.py
│   │   ├── categorization_rules.py
│   │   ├── subcategorization_rules.py
│   │   └── parsing_rules.json
│   └── utils/               # Shared utilities
│       └── __init__.py
├── data/                    # Input and intermediate data (structure remains the same)
│   ├── ...
├── analysis/                # Standalone analysis scripts (not part of the pipeline)
│   ├── __init__.py
│   ├── detect_numeric_patterns.py
│   └── calculate_command_popularity.py
└── README.md                # This file
```

## Pipeline Benefits

- **Interactive**: Review each step before continuing
- **Error Recovery**: Stops on failures so you can fix issues
- **Automated**: No manual file editing required
- **Visual Feedback**: Clear progress indicators and colored output
- **Flexible**: Press 'q' to abort at any review point

## Manual Script Usage

If you need to run individual steps manually, you can run the stage scripts directly. Note that each stage depends on the output of the previous one.

```bash
# Stage 1: Parse a specific snapshot
python Tools/src/stages/1_parse.py <snapshot_filename.txt>

# Stage 2: Classify command types
python Tools/src/stages/2_classify_types.py

# Stage 3: Categorize commands
python Tools/src/stages/3_categorize.py

# Stage 4: Subcategorize commands
python Tools/src/stages/4_subcategorize.py
```

## Analysis Tools (Separate from Pipeline)

These tools analyze existing data and are not part of the main processing pipeline:

```bash
# Detect numeric patterns from pro configs
python Tools/analysis/detect_numeric_patterns.py

# Mark popular commands based on usage
python Tools/analysis/calculate_command_popularity.py
```
