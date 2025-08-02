# Counter-Strike 2 Config Generator

A web-based config generator for Counter-Strike 2, built with Blazor WebAssembly. This tool provides a user-friendly interface to create personalized and server configuration files without manually editing `.cfg` files.

## Features

*   **Dynamic UI:** The user interface is dynamically generated from a JSON schema, ensuring that the available settings are always up-to-date.
*   **Player and Server Configs:** Create both player (`autoexec.cfg`) and server (`server.cfg`) configurations.
*   **Comprehensive Settings:** A wide range of settings are available, from crosshair and viewmodel to server rules and bot behavior.
*   **Downloadable Configs:** Download your generated configuration as a `.cfg` file, ready to be used in-game.
*   **Command Reference:** A reference guide for all available console commands.

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

## Contributing

Contributions are welcome! If you have a suggestion or find a bug, please open an issue. If you would like to contribute code, please open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
