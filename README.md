# Counter-Strike 2 Config Generator

A web-based command reference for Counter-Strike 2, built with Blazor WebAssembly. This tool provides a user-friendly interface to browse and search for console commands.

## Features

*   **Dynamic UI:** The user interface is dynamically generated from a JSON schema, ensuring that the available settings are always up-to-date.
*   **Command Reference:** A reference guide for all available console commands.

## Core Technologies

*   **.NET 9** and **C#**
*   **Blazor WebAssembly** for the frontend framework
*   **Bootstrap 5** for UI styling
*   **Bootstrap Icons** for the icon set
*   **Python** for the command processing pipeline

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

The `Tools/` directory contains Python scripts for parsing and processing Counter-Strike 2 console commands. These tools maintain the JSON schema files that power the application's UI.

### Quick Start - Processing Pipeline

To process a new command snapshot from Counter-Strike 2:

1.  Place your `all_commands-YYYY-DD-MM.txt` file in `Tools/data/`
2.  Run the pipeline: `python Tools/pipeline.py`
3.  Follow the interactive prompts to complete all processing steps

The pipeline will guide you through:
- **Parsing** - Extract commands from the snapshot file.
- **Type Classification** - Determine command data types (bool, float, string, etc.).
- **Master File Creation** - Create a master `commands.json` file for the 'All Commands' UI page.

### Directory Structure

```
Tools/
├── pipeline.py              # Main pipeline runner (START HERE)
├── rules/                   # Classification rules (separated from scripts)
│   ├── type_classification_rules.py      # Rules for determining command data types
│   └── parsing_validation_rules.json     # Rules for validating command parsing
├── scripts/                 # Processing scripts (called by pipeline)
│   ├── parse_commands.py              # Step 1: Parse snapshot file
│   ├── command_classification.py      # Step 2: Classify command data types
│   ├── create_all_commands.py         # Step 3: Create master command file for UI
│   └── parsing_rules.md               # Documentation for command parsing rules
├── utils/                   # Utility scripts and modules
│   └── paths.py                     # Shared path definitions
└── data/                    # Input and intermediate data files
    ├── all_commands-*.txt           # Command snapshots from CS2
    ├── commands.json                # Main processed commands file
```

### Pipeline Benefits

- **Interactive**: Review each step before continuing
- **Error Recovery**: Stops on failures so you can fix issues
- **Automated**: No manual file editing required
- **Visual Feedback**: Clear progress indicators and colored output
- **Flexible**: Press 'q' to abort at any review point

## Contributing

Contributions are welcome! If you have a suggestion or find a bug, please open an issue. If you would like to contribute code, please open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
