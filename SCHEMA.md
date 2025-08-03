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
5. **Unknown Numeric**: Numeric `defaultValue` without decimal point
6. **String**: Any other non-null `defaultValue`

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

## Project File Structure and UI Mapping

The organization of the JSON files directly maps to the layout of the config generator's user interface. This creates a logical and predictable structure for both developers and users.

### The Rule: Folders are Pages, Files are Sections

*   **Top-Level Folders:** Each main folder (`player`, `server`) represents a major page or navigation tab in the application.
*   **JSON Files:** Each JSON file within a folder (`crosshair.json`, `teams.json`, etc.) becomes a distinct section on that page. The filename is used as the title for that section.

### File Structure

```
/
├── player/             (For autoexec.cfg)
│   ├── crosshair.json
│   ├── viewmodel.json
│   ├── hud.json
│   ├── radar.json
│   ├── input.json
│   ├── gameplay.json
│   ├── audio.json
│   ├── communication.json
│   ├── network.json
│   ├── cheats.json
│   ├── actions.json
│   └── misc.json
│   │
│   └── developer/            (Advanced group)
│       ├── rendering.json
│       ├── debugging.json
│       └── spectator.json
│
└── server/             (For server.cfg)
    ├── setup.json
    ├── teams.json
    ├── rounds.json
    ├── objectives.json
    ├── spawning.json
    ├── rules.json
    ├── economy.json
    ├── bots.json
    └── gotv.json
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

## `uiData` Variations by Type

The structure of the `uiData` object changes based on its `type` property. Below are the definitions for each possible type.

### 1\. For `type: "bool"`

Used for simple on/off toggle switches.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Boolean Label",
  "helperText": "Helpful description for this boolean setting.",
  "type": "bool",
  "defaultValue": true,
  "requiresCheats": false,
  "aliasFor": "actual_command_name", // Optional: Indicates this is an alias.
  "visibilityCondition": { // Optional: Controls visibility based on another command.
    "command": "parent_command_name",
    "value": "required_value"
  },
  "deprecated": true // Optional: If the command was removed from the game, can be added to any command
}
```

### 2\. For `type: "integer"`

Used for whole numbers, typically with sliders or steppers.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Integer Label",
  "helperText": "Helpful description for this integer setting.",
  "type": "integer",
  "defaultValue": 10,
  "requiresCheats": false,
  "range": { // Required for this type
    "minValue": 0,
    "maxValue": 100,
    "step": 1
  },
  "aliasFor": "actual_command_name", // Optional: Indicates this is an alias.
  "visibilityCondition": { // Optional: Controls visibility based on another command.
    "command": "parent_command_name",
    "value": "required_value"
  }
}
```

### 3\. For `type: "float"`

Used for numbers with decimal points.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Float Label",
  "helperText": "Helpful description for this float setting.",
  "type": "float",
  "defaultValue": 1.5,
  "requiresCheats": false,
  "range": { // Required for this type
    "minValue": 0.0,
    "maxValue": 10.0,
    "step": 0.1
  },
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```

### 4\. For `type: "string"`

Used for free-form text input.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "String Label",
  "helperText": "Helpful description for this string setting.",
  "type": "string",
  "defaultValue": "default_text",
  "requiresCheats": false,
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```

### 5\. For `type: "enum"`

Used for dropdown menus or radio buttons with a predefined set of options.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Enum Label",
  "helperText": "Helpful description for this enum setting.",
  "type": "enum",
  "defaultValue": "1",
  "options": { // Required for this type
    "0": "Display Value A",
    "1": "Display Value B"
  },
  "requiresCheats": false,
  "aliasFor": "actual_command_name", // Optional: Indicates this is an alias.
  "visibilityCondition": { // Optional: Controls visibility based on another command.
    "command": "parent_command_name",
    "value": "required_value"
  }
}
```

### 6\. For `type: "action"`

Used for action commands that may take arguments.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Action Label",
  "helperText": "Helpful description for this action.",
  "type": "action",
  "defaultValue": null, // Must be null
  "requiresCheats": true,
  "arguments": [ // Optional
    {
      "name": "argument_name",
      "label": "Argument Label",
      "type": "string",
      "placeholder": "e.g. weapon_ak47",
      "required": true
    }
  ],
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```

### 7\. For `type: "bitmask"`

Used for commands where multiple checkbox options are combined into a single integer value.

```json
"uiData": {
  "lastModified": "2025-07-29T05:49:01Z", // ISO 8601 timestamp for when this command was last updated
  "label": "Bitmask Label",
  "helperText": "Select which options to enable.",
  "type": "bitmask",
  "defaultValue": 0,
  "options": { // Required for this type
    "1": "Option A (Value 1)",
    "2": "Option B (Value 2)",
    "4": "Option C (Value 4)"
  },
  "requiresCheats": false,
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```
