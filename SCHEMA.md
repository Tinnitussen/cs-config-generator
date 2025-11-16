# CS2 Config Schema Documentation

This document defines the JSON schema used for all command configuration files in this project. The goal is to create a clear separation between raw data extracted from the game and the curated data used to build the user interface.

## Command Processing Pipeline

Commands are processed through an automated pipeline that transforms raw CS2 console data into the structured JSON schema used by the config generator.

### Processing Steps

The pipeline (`Tools/pipeline.py`) guides you through these steps:

1.  **Parse Commands** - Extract and validate commands from CS2 snapshot files.
2.  **Classify Types** - Determine command data types (bool, float, string, etc.) using rule-based logic.
3.  **Classify by Popularity** - Identify popular `player` and `server` commands by analyzing professional and community config files.
4.  **Create 'All Commands' File** - Generate a master JSON file containing all commands for the UI.
5.  **Subcategorize** - Organize the popular Player and Server commands into UI sections (e.g., crosshair, viewmodel, etc.).

### Classification Rules

Command processing uses a rules-based system with logic separated into dedicated rule files:

#### Type Classification (`Tools/rules/type_classification_rules.py`)
Commands are classified by applying these rules in order:
1. **Action**: `defaultValue` is `null`
2. **Bool**: `defaultValue` is `"true"` or `"false"`
3. **Bitmask**: Description contains `"bitmask"`
4. **Float**: Numeric `defaultValue` with decimal point
5. **String**: Any other non-null `defaultValue`

#### Popularity Classification (`Tools/rules/popularity_rules.py`)
A command is classified as `player` or `server` if it appears in a significant percentage of the respective configuration files. This is controlled by the `POPULARITY_THRESHOLD` in the rules file.

#### Subcategorization Rules
- **Player** (`Tools/rules/player_subcategorization_rules.py`): crosshair, viewmodel, hud, audio, etc.
- **Server** (`Tools/rules/server_subcategorization_rules.py`): setup, teams, rounds, economy, etc.

### Running the Pipeline

To process a new command snapshot:

```bash
cd Tools/
python pipeline.py
```

The pipeline will:
1. Let you select a snapshot file
2. Run each processing step
3. Wait for your review after each step
4. Allow you to abort with 'q' if issues are found

### Data Flow

```
all_commands-YYYY-DD-MM.txt (Raw CS2 data)
    ↓ parse_commands.py
commands.json (Structured with consoleData)
    ↓ command_classification.py
commands.json (+ uiData with types)
    ↓ command_popularity.py
classified_commands/player_commands.json
classified_commands/server_commands.json
    ↓ subcategorization/subcategorize_*.py
CSConfigGenerator/wwwroot/data/commandschema/player/*.json
CSConfigGenerator/wwwroot/data/commandschema/server/*.json
    ↓ create_all_commands.py
CSConfigGenerator/wwwroot/data/commandschema/all/all_commands.json
```

## Project File Structure

The `all_commands.json` file, located in the `all/` directory, contains a comprehensive list of all commands for the 'All Commands' UI tab. This file serves as the primary data source for the application's user interface.

### File Structure

```
/
└── all/
    └── all_commands.json (Contains all commands for the 'All Commands' UI tab)
```

---

## Common Command Structure

Every command object in a JSON configuration file follows this base structure. The `uiData` object is the only part that changes based on the command's `type`.

| Property      | Type   | Description                                       |
| :------------ | :----- | :------------------------------------------------ |
| `command`     | String | The exact name of the console command or variable. |
| `consoleData` | Object | Contains raw, unmodified data from the console.   |
| `uiData`      | Object | Contains curated data for building the UI.        |

### `consoleData` Object

This object serves as the "source of truth," containing only data parsed directly from the game's console. It has the following structure:

```json
"consoleData": {
  "sourcedAt": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this data was pulled from the game console
  "defaultValue": "raw_value_from_console (string or null)",
  "flags": [ "flag1", "flag2" ],
  "description": "The raw description text from the console.",
}
````

-----

## `uiData` Object Structure

The `uiData` object is designed to be flexible and cater to the specific needs of different command types. This is achieved through a class hierarchy where a base `UiData` class holds the common properties, and concrete subclasses add the properties that are specific to that command type.

### Common Properties

All `uiData` objects, regardless of their type, will have the following properties:

| Property         | Type    | Description                                       |
| :--------------- | :------ | :------------------------------------------------ |
| `label`          | String  | The user-friendly name for the command.           |
| `helperText`     | String  | A description of the command's purpose.           |
| `type`           | String  | The type of the command (e.g., "bool", "integer"). |
| `requiresCheats` | Boolean | Whether the command requires `sv_cheats` to be enabled. |

### Type-Specific Properties

Depending on the `type` of the command, the `uiData` object will have additional properties.

#### For `type: "bool"`

| Property       | Type    | Description                   |
| :------------- | :------ | :---------------------------- |
| `defaultValue` | Boolean | The default value of the command. |

#### For `type: "integer"`

| Property       | Type   | Description                   |
| :------------- | :----- | :---------------------------- |
| `defaultValue` | Int    | The default value of the command. |
| `range`        | Object | The range of allowed values.  |

#### For `type: "float"`

| Property       | Type   | Description                   |
| :------------- | :----- | :---------------------------- |
| `defaultValue` | Float  | The default value of the command. |
| `range`        | Object | The range of allowed values.  |

#### For `type: "string"`

| Property       | Type   | Description                   |
| :------------- | :----- | :---------------------------- |
| `defaultValue` | String | The default value of the command. |

#### For `type: "enum"`

| Property       | Type   | Description                        |
| :------------- | :----- | :--------------------------------- |
| `defaultValue` | String | The default value of the command.      |
| `options`      | Object | The available options for the command. |

#### For `type: "action"`

This command type has no additional properties.

#### For `type: "bitmask"`

| Property       | Type   | Description                        |
| :------------- | :----- | :--------------------------------- |
| `defaultValue` | Int    | The default value of the command.      |
| `options`      | Object | The available options for the command. |

#### For `type: "unknown"`

This type is used for commands that appear to be numeric but cannot be definitively classified as `integer` or `float` from the console data alone. It is safe to assume this is a numeric type.

| Property       | Type   | Description                   |
| :------------- | :----- | :---------------------------- |
| `defaultValue` | Number | The default value of the command. |
