using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Represents the complete definition for a single console variable (cvar).
/// This class is designed to be deserialized from your JSON schema files.
/// </summary>
public record CommandDefinition
{
    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("description")]
    public required string Description { get; init; }

    [JsonPropertyName("type")]
    [JsonConverter(typeof(SettingTypeJsonConverter))]
    public required SettingType Type { get; init; }

    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    [JsonPropertyName("requiresCheats")]
    public bool RequiresCheats { get; init; }

    // New property for advanced/uncommon commands
    [JsonPropertyName("hideFromDefaultView")]
    public bool HideFromDefaultView { get; init; }

    // Numeric constraints
    [JsonPropertyName("minValue")]
    public float? MinValue { get; init; }

    [JsonPropertyName("maxValue")]
    public float? MaxValue { get; init; }

    [JsonPropertyName("step")]
    public float? Step { get; init; }

    // Enum options
    [JsonPropertyName("options")]
    public Dictionary<string, string>? Options { get; init; }

    // UI metadata for extensibility
    [JsonPropertyName("ui")]
    public JsonElement? UiMetadata { get; init; }
}