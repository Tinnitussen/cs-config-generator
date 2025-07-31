# Gemini Context

This file provides context for Gemini to understand the project.

## Project: cs-config-generator

A web-based config generator for Counter-Strike 2.

## Project Analysis

### Project Overview

This is a Blazor WebAssembly application designed to generate Counter-Strike 2 configuration files. It allows users to modify settings for both player and server configurations, which are then compiled into a downloadable `.cfg` file. The application is deployed to GitHub Pages.

### Core Technologies

*   **Framework:** Blazor WebAssembly (standalone)
*   **Language:** C#
*   **.NET Version:** 9.0
*   **UI:** Standard Blazor components with custom CSS. It does not appear to be using a UI library like MudBlazor or Blazorise.
*   **Deployment:** GitHub Actions to GitHub Pages.

### Project Structure and Key Components

*   **`CSConfigGenerator.csproj`**: Confirms this is a Blazor WebAssembly project targeting .NET 9.0. It includes the necessary packages for Blazor WebAssembly development.
*   **`Program.cs`**: This is the application's entry point.
    *   It registers services for dependency injection, including `HttpClient`, `ISchemaService`, `ToastService`, and `IConfigStateService`.
    *   It initializes the `ISchemaService` and `IConfigStateService` before the application runs.
    *   It appears to be using keyed services to differentiate between player and server config state services, although the server-side one is currently commented out.
*   **`App.razor`**: The root component of the application. It sets up the Blazor `Router` to handle navigation.
*   **`wwwroot/data/commandschema/`**: This directory is crucial. It contains the JSON definitions for all the available settings, separated into categories for both player and server. This is the "source of truth" for what the user can configure.
*   **`Components/`**: This directory contains reusable Blazor components.
    *   **`ConfigEditor.razor`**: This is likely the main UI for displaying and editing the configuration settings.
    *   **`Dynamic/`**: The components in this subdirectory (`DynamicForm.razor`, `DynamicInput.razor`, `ConfigSectionGroup.razor`) are responsible for dynamically generating the UI based on the JSON schema. This is a key architectural pattern in the application.
*   **`Services/`**: This directory contains the application's services.
    *   **`ISchemaService` / `SchemaService.cs`**: Responsible for fetching and parsing the JSON schema files from `wwwroot/data/commandschema/`.
    *   **`IConfigStateService` / `PlayerConfigStateService.cs` / `ServerConfigStateService.cs`**: These services manage the state of the configuration settings. They hold the current values of the settings and provide methods for modifying them.
    *   **`ToastService.cs`**: A service for displaying toast notifications.
*   **`Pages/`**: This directory contains the routable pages of the application.
    *   **`PlayerConfig.razor`** and **`ServerConfig.razor`**: These pages likely host the `ConfigEditor` component and are the main entry points for the user to create their configurations.
*   **`.github/workflows/deploy.yml`**: This file defines the CI/CD pipeline. It builds the Blazor application, publishes it, and deploys it to GitHub Pages. It also contains a step to rewrite the base `href` in `index.html`, which is a common practice for deploying Blazor apps to a subdirectory on a domain.

### Inferred Architecture and Data Flow

1.  **Initialization**: When the application starts, `Program.cs` initializes the `SchemaService` and the `PlayerConfigStateService`.
2.  **Schema Loading**: The `SchemaService` fetches the JSON files from the `wwwroot/data/commandschema/` directory and parses them into a data structure that the application can use.
3.  **UI Rendering**: The user navigates to either the `PlayerConfig` or `ServerConfig` page.
4.  **Dynamic Form Generation**: The `ConfigEditor` component, along with the dynamic components, uses the loaded schema to generate the appropriate input fields (text boxes, sliders, dropdowns, etc.) for each setting.
5.  **State Management**: The `PlayerConfigStateService` (or `ServerConfigStateService`) holds the current values of all the settings. When the user changes a value in the UI, the corresponding property in the state service is updated.
6.  **Config Generation**: There is likely a mechanism (perhaps a "Download" or "Generate" button) that takes the current state from the `IConfigStateService`, formats it into the correct `.cfg` file syntax, and makes it available for the user to download.