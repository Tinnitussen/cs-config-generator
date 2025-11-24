# Project Context for AI Assistants

High-level context for the CS2 Config Generator project.

## Overview

**Type**: Blazor WebAssembly standalone app (no backend)
**Purpose**: Counter-Strike 2 console command reference and config tool
**Stack**: .NET 10.0, Bootstrap 5, System.Text.Json
**Deployment**: GitHub Pages (static hosting)

## Architecture

**Pattern**: Service-oriented with dependency injection

```
JSON Data (wwwroot/data/)
  → SchemaService (command definitions)
  → UserConfigService (user values)
  → LocalStorageService (browser persistence)
  → UI Components
```

**Key Layers**:
- `Services/` - Business logic (5 scoped services)
- `Components/` - Reusable UI (ConfigEditor, Modal, ToastContainer, etc.)
- `Pages/` - Routable views (Home, CommandReference)
- `Models/` - Data structures (class hierarchy for type safety)

## Data Model

**Command Structure**: `CommandDefinition` has three parts:
- `command` - Command name
- `consoleData` - Raw CS2 console data
- `uiData` - Type-specific UI data (polymorphic class hierarchy)

**Type System**: Abstract `UiData` base class with 13 concrete types (BoolUiData, IntegerUiData, FloatUiData, etc.). Custom JSON converter handles polymorphic deserialization.

See `PROPOSAL.md` for class hierarchy rationale.

## Setup

Install .NET 10 SDK:
```bash
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x ./dotnet-install.sh
./dotnet-install.sh --channel 10.0
export PATH=$PATH:$HOME/.dotnet
```

Build/Test:
```bash
dotnet build
dotnet test
```

## Coding Standards

**CSS Units**: Prefer `rem` (global sizing) and `em` (component-relative) over `px` (use only for borders/fixed elements)

**C# Conventions**: File-scoped namespaces, records for immutability, nullable enabled, init properties
**Blazor Patterns**: No code-behind, use `.razor.css` for scoped styles, `@inject` for services
**Naming**: `IServiceName` interfaces, `ServiceNameService` implementations

## Quick Reference

**Data Location**: `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`
**Pipeline**: Separate Python project - see `PIPELINE.md`

## Documentation

- `README.md` - Setup and overview
- `SCHEMA.md` - JSON schema spec
- `PIPELINE.md` - Data generation pipeline
- `PROPOSAL.md` - Design decisions
