# Counter-Strike 2 Config Generator

A web-based command reference for Counter-Strike 2, built with Blazor WebAssembly. This tool provides a user-friendly interface to browse and search for console commands.

## Features

*   **Dynamic UI:** The user interface is dynamically generated from a JSON schema, ensuring that the available settings are always up-to-date.
*   **Command Reference:** A reference guide for all available console commands.

## Core Technologies

*   **.NET 10** and **C#**
*   **Blazor WebAssembly** for the frontend framework
*   **Bootstrap 5** for UI styling
*   **Bootstrap Icons** for the icon set
*   **Python** for the command processing pipeline

## For Developers

This project is built with .NET 10 and Blazor WebAssembly. The core of the application is the `CSConfigGenerator` project.

### Project Structure

*   `CSConfigGenerator/`: The main Blazor WebAssembly project.
*   `CSConfigGenerator/wwwroot/data/commandschema/`: Contains the JSON schema files that define the available settings. This is the "source of truth" for the application.
*   `CSConfigGenerator/Services/`: Contains the services that manage the application's state and logic.
*   `CSConfigGenerator/Components/`: Contains the reusable Blazor components that make up the UI.
*   `CommandPipeline/`: Contains Python scripts for parsing and classifying commands from the game.
*   `SCHEMA.md`: Provides detailed documentation on the JSON schema used for the command configuration files.

### Getting Started

1.  Clone the repository.
2.  Install the .NET 10 SDK.
3.  Open the `CSConfigGenerator.slnx` solution file in your preferred IDE.
4.  Run the `CSConfigGenerator` project.

### JSON Schema

The application's UI is dynamically generated from a set of JSON files located in `CSConfigGenerator/wwwroot/data/commandschema/`. The structure of these files is documented in `SCHEMA.md`.

### Data Processing Pipeline

The `CommandPipeline/` directory contains a standalone Python project for processing Counter-Strike 2 console commands and generating the JSON schema files.

**For maintainers**: If you need to update the command data from a new CS2 snapshot, see `PIPELINE.md` for complete documentation on running the data processing pipeline.

## Documentation

- **[SCHEMA.md](SCHEMA.md)** - JSON schema specification for command data files
- **[PIPELINE.md](PIPELINE.md)** - Command processing pipeline documentation (for maintainers)
- **[PROPOSAL.md](PROPOSAL.md)** - Technical design decisions and architecture rationale
- **[AGENTS.md](AGENTS.md)** - Project context for AI coding assistants

## Contributing

Contributions are welcome! If you have a suggestion or find a bug, please open an issue. If you would like to contribute code, please open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
