# Counter-Strike 2 Config Generator

Blazor WebAssembly app for browsing CS2 console commands and building `.cfg` files in a VS Code–style editor.

## What it does

- **Command reference**: Browse/search CS2 cvars/commands.
- **Config workspace**: Edit configs, save them to browser storage, download/copy/upload `.cfg` files.
- **Presets**: Load example `.cfg` presets (players + servers).
- **Schema-driven UI**: Command UI is generated from JSON data in `CSConfigGenerator/wwwroot/data/`.

## How data loading works

- **Entry point**: `CSConfigGenerator/wwwroot/data/manifest.json` lists one or more command data JSON files.
- **Command data**: Currently `CSConfigGenerator/wwwroot/data/commandschema/all_commands.json`.
- **Runtime loader**: `SchemaService` reads the manifest and loads each listed file.

The command data format is documented in `SCHEMA.md`.

## Repository layout

- **`CSConfigGenerator/`**: Blazor WebAssembly frontend app.
- **`CSConfigGenerator/wwwroot/data/`**: Static data shipped with the app (manifest, command schema, presets).
- **`CommandPipeline/`**: Python pipeline to regenerate command data from a CS2 snapshot.
- **`CSConfigGenerator.Tests/`**: Unit tests for core logic.

## Quick start (dev)

Prerequisite: **.NET SDK 10**.

```bash
dotnet restore
dotnet run --project CSConfigGenerator
```

## Updating the command data (maintainers)

1. Put a CS2 `dump_commands` snapshot into `CommandPipeline/data/` (file name must match `all_commands-*.txt`).
2. Run the pipeline:

```bash
python CommandPipeline/pipeline.py
```

See `PIPELINE.md` for details (including non-interactive mode and optional scraping inputs).

## Data sources & attribution notes

This repo may include third-party data files under `CommandPipeline/data/` (for example config samples and an HTML snapshot used for scraping). If you redistribute the repository or the generated data, make sure you’re comfortable with the provenance and licensing of those inputs.

## Deploying to GitHub Pages

This repo is set up as a static site (Blazor WASM) and includes `CSConfigGenerator/wwwroot/404.html` to support client-side routing on GitHub Pages.

For **project pages** (`https://username.github.io/repo-name/`), publish with a base href:

```bash
dotnet publish CSConfigGenerator -c Release -p:BaseHref=/repo-name/
```

Then serve the publish output via GitHub Pages (for example from a `gh-pages` branch or a `docs/` folder, depending on your Pages settings).

## Documentation

- **[SCHEMA.md](SCHEMA.md)**: JSON format consumed by the app
- **[PIPELINE.md](PIPELINE.md)**: How to regenerate `wwwroot/data/commandschema/*.json`
- **[PROPOSAL.md](PROPOSAL.md)**: Rationale for the polymorphic `UiData` model
- **[AGENTS.md](AGENTS.md)**: Project context + conventions (for AI coding assistants)

## Contributing

Open an issue for bugs/ideas; PRs welcome.

## License

MIT — see `LICENSE`.
