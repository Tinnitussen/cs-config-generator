# Proposal: Redesigning the Command Datastructure

## 1. The Problem with the Current Datastructure

The current command datastructure, while functional, suffers from a lack of type safety and clarity. The `UiData` class uses a single, monolithic structure to represent all command types, from simple booleans to complex bitmasks. This is achieved by using a `type` property and a number of optional properties that may or may not be relevant for a given command.

This approach has several disadvantages:

*   **Lack of Type Safety:** There is no way to enforce at compile time that a `UiData` object of type `"integer"` will have a `range` property. This can lead to runtime errors and makes the code more difficult to reason about.
*   **Difficult to Validate:** It's challenging to validate that a given `UiData` object is well-formed. For example, a `bitmask` command must have an `options` property, but this is not enforced by the C# type system.
*   **Poor Discoverability:** When working with a `UiData` object, it's not immediately clear which properties are relevant for a given command type. This makes the code harder to understand and maintain.
*   **Scalability Issues:** Adding a new command type requires modifying the `UiData` class and adding more optional properties, further complicating the structure.

## 2. The Proposed Solution: A Class Hierarchy

To address these issues, I propose a new datastructure based on a class hierarchy with an abstract base class and concrete subclasses for each command type. This will provide a more robust, type-safe, and maintainable solution.

### 2.1. The New `UiData` Base Class

The `UiData` class will be an abstract base class that contains the common properties shared by all command types. It will also include an abstract `Type` property that will be overridden by the concrete subclasses.

```csharp
[JsonConverter(typeof(UiDataJsonConverter))]
public abstract record UiData
{
    [JsonPropertyName("label")]
    public required string Label { get; init; }

    [JsonPropertyName("helperText")]
    public string HelperText { get; init; } = string.Empty;

    [JsonPropertyName("type")]
    public abstract SettingType Type { get; }

    [JsonPropertyName("requiresCheats")]
    public bool RequiresCheats { get; init; }
}
```

### 2.2. Concrete Subclasses for Each Command Type

Each command type will have its own concrete subclass that inherits from the `UiData` base class. These subclasses will add the properties that are specific to that command type.

Here are the proposed subclasses:

**For `type: "bool"`**

```csharp
public record BoolUiData : UiData
{
    public override SettingType Type => SettingType.Bool;

    [JsonPropertyName("defaultValue")]
    public bool DefaultValue { get; init; }
}
```

**For `type: "integer"`**

```csharp
public record IntegerUiData : UiData
{
    public override SettingType Type => SettingType.Integer;

    [JsonPropertyName("defaultValue")]
    public int DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }
}
```

**For `type: "float"`**

```csharp
public record FloatUiData : UiData
{
    public override SettingType Type => SettingType.Float;

    [JsonPropertyName("defaultValue")]
    public float DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }
}
```

**For `type: "string"`**

```csharp
public record StringUiData : UiData
{
    public override SettingType Type => SettingType.String;

    [JsonPropertyName("defaultValue")]
    public required string DefaultValue { get; init; }
}
```

**For `type: "command"`**

```csharp
public record CommandUiData : UiData
{
    public override SettingType Type => SettingType.Command;
}
```

**For `type: "bitmask"`**

```csharp
public record BitmaskUiData : UiData
{
    public override SettingType Type => SettingType.Bitmask;

    [JsonPropertyName("defaultValue")]
    public int DefaultValue { get; init; }

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }
}
```

### 2.3. Custom `JsonConverter`

To make this work with `System.Text.Json`, we will need to create a custom `JsonConverter` that can deserialize the JSON into the correct subclass based on the `type` property.

```csharp
public class UiDataJsonConverter : JsonConverter<UiData>
{
    public override UiData Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        // Implementation details omitted for brevity
    }

    public override void Write(Utf8JsonWriter writer, UiData value, JsonSerializerOptions options)
    {
        // Implementation details omitted for brevity
    }
}
```

## 3. "Before and After" Comparison

Here is a comparison of the current and proposed datastructures for an `"int"` command.

### Before

**C#**

```csharp
public record UiData
{
    // ... other properties
    public required SettingType Type { get; init; }
    public required JsonElement DefaultValue { get; init; }
    public NumericRange? Range { get; init; }
    // ... other properties
}
```

**JSON**

```json
{
  "uiData": {
    "label": "Integer Label",
    "type": "int",
    "defaultValue": 10,
    "range": {
      "minValue": 0,
      "maxValue": 100,
      "step": 1
    }
  }
}
```

### After

**C#**

```csharp
public record IntegerUiData : UiData
{
    public override SettingType Type => SettingType.Int;
    public int DefaultValue { get; init; }
    public required NumericRange Range { get; init; }
}
```

**JSON**

The JSON structure remains the same, which means no changes are needed to existing data files.

```json
{
  "uiData": {
    "label": "Integer Label",
    "type": "int",
    "defaultValue": 10,
    "range": {
      "minValue": 0,
      "maxValue": 100,
      "step": 1
    }
  }
}
```

## 4. Benefits of the New Datastructure

*   **Improved Type Safety:** The new datastructure will enforce at compile time that a `UiData` object of a given type will have the correct properties.
*   **Easier to Validate:** It will be much easier to validate that a given `UiData` object is well-formed.
*   **Improved Discoverability:** When working with a `UiData` object, it will be immediately clear which properties are relevant for a given command type.
*   **Better Scalability:** Adding a new command type will be as simple as creating a new subclass.
*   **No Changes to JSON:** The new datastructure will not require any changes to our existing JSON data files.

By adopting this new datastructure, we can create a more robust, maintainable, and scalable foundation for the command reference UI.
