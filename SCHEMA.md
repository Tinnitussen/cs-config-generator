# CS2 Config Schema Documentation

This document defines the JSON schema used for all command configuration files in this project. The goal is to create a clear separation between raw data extracted from the game and the curated data used to build the user interface.

## Project File Structure and UI Mapping

The organization of the JSON files directly maps to the layout of the config generator's user interface. This creates a logical and predictable structure for both developers and users.

### The Rule: Folders are Pages, Files are Sections

* **Top-Level Folders:** Each main folder (`PlayerConfig`, `ServerConfig`, etc.) represents a major page or navigation tab in the application.
* **JSON Files:** Each JSON file within a folder (`crosshair.json`, `teams.json`, etc.) becomes a distinct section on that page. The filename is used as the title for that section.

### File Structure

```

/
├── PlayerConfig/         (-\> "Player" Page)
│   ├── crosshair.json    (-\> "Crosshair" Section)
│   ├── viewmodel.json    (-\> "Viewmodel" Section)
│   ├── hud.json
│   ├── radar.json
│   ├── input.json
│   ├── audio.json
│   ├── network.json
│   └── misc.json
│
├── ServerConfig/         (-\> "Server" Page)
│   ├── setup.json
│   ├── teams.json
│   ├── rounds.json
│   ├── objectives.json
│   ├── spawning.json
│   ├── rules.json
│   ├── economy.json
│   ├── bots.json
│   └── gotv.json
│
├── PracticeConfig/       (-\> "Practice" Page)
│   ├── cheats.json
│   └── utilities.json
│
└── Developer/            (-\> "Developer" Page)
├── debugging.json
├── navigation.json
└── rendering.json

````

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
  "defaultValue": "raw_value_from_console (string or null)",
  "flags": [ "flag1", "flag2" ],
  "description": "The raw description text from the console."
}
````

-----

## `uiData` Variations by Type

The structure of the `uiData` object changes based on its `type` property. Below are the definitions for each possible type.

### 1\. For `type: "boolean"`

Used for simple on/off toggle switches.

```json
"uiData": {
  "label": "Boolean Label",
  "helperText": "Helpful description for this boolean setting.",
  "type": "boolean",
  "defaultValue": true,
  "requiresCheats": false,
  "hideFromDefaultView": false,
  "aliasFor": "actual_command_name", // Optional: Indicates this is an alias.
  "visibilityCondition": { // Optional: Controls visibility based on another command.
    "command": "parent_command_name",
    "value": "required_value"
  }
}
```

### 2\. For `type: "integer"`

Used for whole numbers, typically with sliders or steppers.

```json
"uiData": {
  "label": "Integer Label",
  "helperText": "Helpful description for this integer setting.",
  "type": "integer",
  "defaultValue": 10,
  "requiresCheats": false,
  "hideFromDefaultView": false,
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
  "label": "Float Label",
  "helperText": "Helpful description for this float setting.",
  "type": "float",
  "defaultValue": 1.5,
  "requiresCheats": false,
  "hideFromDefaultView": false,
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
  "label": "String Label",
  "helperText": "Helpful description for this string setting.",
  "type": "string",
  "defaultValue": "default_text",
  "requiresCheats": false,
  "hideFromDefaultView": false,
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```

### 5\. For `type: "enum"`

Used for dropdown menus or radio buttons with a predefined set of options.

```json
"uiData": {
  "label": "Enum Label",
  "helperText": "Helpful description for this enum setting.",
  "type": "enum",
  "defaultValue": "1",
  "options": { // Required for this type
    "0": "Display Value A",
    "1": "Display Value B"
  },
  "requiresCheats": false,
  "hideFromDefaultView": false,
  "aliasFor": "actual_command_name", // Optional: Indicates this is an alias.
  "visibilityCondition": { // Optional: Controls visibility based on another command.
    "command": "parent_command_name",
    "value": "required_value"
  }
}
```

### 6\. For `type: "command"`

Used for action commands that may take arguments.

```json
"uiData": {
  "label": "Action Label",
  "helperText": "Helpful description for this action.",
  "type": "command",
  "defaultValue": null, // Must be null
  "requiresCheats": true,
  "hideFromDefaultView": false,
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
  "hideFromDefaultView": false,
  "aliasFor": "actual_command_name" // Optional: Indicates this is an alias.
}
```