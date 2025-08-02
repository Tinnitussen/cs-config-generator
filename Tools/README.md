# Command Processing Pipeline

This directory contains a Python-based pipeline for processing Counter-Strike 2 console commands. The goal of this pipeline is to take a raw text dump of commands from the game, process and classify them, and ultimately generate a set of structured JSON schema files that are consumed by the CSConfigGenerator web application.

## The New, Refactored Pipeline

The pipeline has been refactored into a cohesive package located in the `Tools/pipeline/` directory. It is designed to be run from a single entry point and is driven by a series of modular steps and rule files.

### How to Run the Pipeline

To run the entire pipeline from start to finish, execute the main orchestration script from the repository root:

```bash
python Tools/pipeline/run_pipeline.py
```

This script will automatically execute all the necessary steps in the correct order.

### Pipeline Architecture

The pipeline is composed of several steps, each located in its own file within `Tools/pipeline/steps/`. The orchestrator calls each step in sequence.

1.  **Step 1: Parse Raw Commands (`step1_parse.py`)**
    *   **Input**: A raw text file of commands (e.g., `Tools/data/all_commands-*.txt`).
    *   **Output**: A consolidated `Tools/data/commands.json` file.
    *   **Function**: Reads the raw text dump, parses each line into a command, default value, flags, and description. It compares against the existing `commands.json` to identify and flag new, updated, or deprecated commands.

2.  **Step 2: Classify Command Types (`step2_classify_types.py`)**
    *   **Input**: `Tools/data/commands.json`.
    *   **Output**: `Tools/data/commands.json` (updated in-place).
    *   **Function**: Adds a `uiData` object to each command. It then uses rules defined in `Tools/rules/type_classification_rules.py` to determine the command's data type (e.g., `bool`, `float`, `string`, `action`).

3.  **Step 3: Split by Primary Category (`step3_split_by_category.py`)**
    *   **Input**: `Tools/data/commands.json`.
    *   **Output**: Categorized files like `player_commands.json`, `server_commands.json`, etc., in `Tools/data/classified_commands/`.
    *   **Function**: Splits the commands into broad, primary categories based on rules in `Tools/rules/splitting_rules.py`.

4.  **Step 4: Sub-categorize (`step4_subcategorize.py`)**
    *   **Input**: The categorized files from the previous step.
    *   **Output**: The final, fine-grained JSON schema files in `CSConfigGenerator/wwwroot/data/commandschema/`.
    *   **Function**: This is a rule-driven step that processes each primary category. It uses the rules defined in `Tools/pipeline/subcategorization_rules.json` to sort commands into their final UI-facing categories (e.g., `crosshair`, `viewmodel`, `network`).

### Modifying the Pipeline

*   **To change parsing validation**: Edit `Tools/rules/parsing_validation_rules.json`.
*   **To change how command types are inferred**: Modify the functions in `Tools/rules/type_classification_rules.py`.
*   **To change how commands are split into player/server/shared**: Modify `Tools/rules/splitting_rules.py`.
*   **To change how commands are sub-categorized for the UI**: Edit the main rules file at `Tools/pipeline/subcategorization_rules.json`. This is the most common place for changes.
