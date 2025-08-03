# Counter-Strike 2 Config Generator

A web-based config generator for Counter-Strike 2, built with Blazor WebAssembly. This tool provides a user-friendly interface to create personalized and server configuration files without manually editing `.cfg` files.

## Features

*   **Dynamic UI:** The user interface is dynamically generated from a JSON schema, ensuring that the available settings are always up-to-date.
*   **Player and Server Configs:** Create both player (`autoexec.cfg`) and server (`server.cfg`) configurations.
*   **Comprehensive Settings:** A wide range of settings are available, from crosshair and viewmodel to server rules and bot behavior.
*   **Downloadable Configs:** Download your generated configuration as a `.cfg` file, ready to be used in-game.
*   **Command Reference:** A reference guide for all available console commands.

## Core Technologies

*   **.NET 9** and **C#**
*   **Blazor WebAssembly** for the frontend framework
*   **Bootstrap 5** for UI styling
*   **Bootstrap Icons** for the icon set
*   **Python** for the command processing pipeline

## How to Use

1.  Navigate to the deployed application on GitHub Pages.
2.  Select either **Player Config** or **Server Config** from the navigation menu.
3.  Customize the settings using the provided UI controls.
4.  Click the **Download** button to get your generated `.cfg` file.
5.  Place the downloaded file in the appropriate Counter-Strike 2 directory.

## For Developers

This project is built with .NET 9 and Blazor WebAssembly. The core of the application is the `CSConfigGenerator` project.

### Project Structure

*   `CSConfigGenerator/`: The main Blazor WebAssembly project.
*   `CSConfigGenerator/wwwroot/data/commandschema/`: Contains the JSON schema files that define the available settings. This is the "source of truth" for the application.
*   `CSConfigGenerator/Services/`: Contains the services that manage the application's state and logic.
*   `CSConfigGenerator/Components/`: Contains the reusable Blazor components that make up the UI.
*   `Tools/`: Contains Python scripts for parsing and classifying commands from the game.
*   `SCHEMA.md`: Provides detailed documentation on the JSON schema used for the command configuration files.

### Getting Started

1.  Clone the repository.
2.  Install the .NET 9 SDK.
3.  Open the `CSConfigGenerator.slnx` solution file in your preferred IDE.
4.  Run the `CSConfigGenerator` project.

### JSON Schema

The application's UI is dynamically generated from a set of JSON files located in `CSConfigGenerator/wwwroot/data/commandschema/`. To add or modify settings, you will need to edit these files. The structure of these files is documented in `SCHEMA.md`.

## Tools Directory

The `Tools/` directory contains Python scripts for parsing and processing Counter-Strike 2 console commands. These tools maintain the JSON schema files that power the config generator's UI.

### Quick Start - Processing Pipeline

To process a new command snapshot from Counter-Strike 2:

1. Place your `all_commands-YYYY-DD-MM.txt` file in `Tools/data/`
2. Run the pipeline: `python Tools/pipeline.py`
3. Follow the interactive prompts to complete all processing steps

The pipeline will guide you through:
- **Parsing** - Extract commands from the snapshot file
- **Classification** - Determine command types (bool, float, string, etc.)
- **Categorization** - Split commands into player/server/shared groups
- **Subcategorization** - Organize commands into UI sections

### Directory Structure

```
Tools/
├── pipeline.py              # Main pipeline runner (START HERE)
├── rules/                   # Classification rules (separated from scripts)
│   ├── type_classification_rules.py      # Rules for determining command types
│   ├── splitting_rules.py                # Rules for player/server/shared classification
│   ├── numeric_detection_rules.py        # Rules for detecting numeric types
│   ├── player_subcategorization_rules.py # Rules for player command sections
│   ├── server_subcategorization_rules.py # Rules for server command sections
│   ├── shared_subcategorization_rules.py # Rules for shared command sections
│   ├── popularity_rules.py               # Rules for marking popular commands
│   └── parsing_validation_rules.json     # Validation rules for parsing
├── scripts/                 # Processing scripts (called by pipeline)
│   ├── parse_commands.py              # Step 1: Parse snapshot file
│   ├── command_classification.py      # Step 2: Classify command types
│   └── splitting/
│       ├── classify_commands.py       # Step 3: Split into categories
│       └── subcategorization/         # Step 4: Create UI sections
│           ├── subcategorize_player.py
│           ├── subcategorize_server.py
│           └── subcategorize_shared.py
├── scripts/classify-from-existing/    # Separate analysis tools (not part of main pipeline)
│   ├── numeric_detection.py          # Analyze config files for numeric patterns
│   └── command_popularity.py         # Mark popular commands based on pro configs
└── data/                    # Input and intermediate data files
    ├── all_commands-*.txt           # Command snapshots from CS2
    ├── commands.json                # Main processed commands file
    ├── classified_commands/         # Commands split by category
    └── pro-player-configs/          # Pro player configs for analysis
```

### Pipeline Benefits

- **Interactive**: Review each step before continuing
- **Error Recovery**: Stops on failures so you can fix issues
- **Automated**: No manual file editing required
- **Visual Feedback**: Clear progress indicators and colored output
- **Flexible**: Press 'q' to abort at any review point

### Manual Script Usage

If you need to run individual steps manually:

```bash
# Parse a specific snapshot
python Tools/scripts/parse_commands.py

# Classify command types
python Tools/scripts/command_classification.py

# Split into categories
python Tools/scripts/splitting/classify_commands.py

# Subcategorize (run all three)
python Tools/scripts/splitting/subcategorization/subcategorize_player.py
python Tools/scripts/splitting/subcategorization/subcategorize_server.py
python Tools/scripts/splitting/subcategorization/subcategorize_shared.py
```

### Analysis Tools (Separate from Pipeline)

These tools analyze existing data and are not part of the main processing pipeline:

```bash
# Detect numeric patterns from pro configs
python Tools/scripts/classify-from-existing/numeric_detection.py

# Mark popular commands based on usage
python Tools/scripts/classify-from-existing/command_popularity.py
```

## Contributing

Contributions are welcome! If you have a suggestion or find a bug, please open an issue. If you would like to contribute code, please open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
