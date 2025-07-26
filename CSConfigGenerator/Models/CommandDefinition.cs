using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Represents the complete definition for a single console variable (cvar).
/// This class is designed to be deserialized from your JSON schema files.
/// </summary>
public class CommandDefinition
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public CommandValueType Type { get; set; }

    [JsonPropertyName("defaultValue")]
    public object? DefaultValue { get; set; }

    [JsonPropertyName("requiresCheats")]
    public bool RequiresCheats { get; set; }

    // --- Numeric-specific properties ---
    // These will be null if the type is not 'numeric'.
    [JsonPropertyName("minValue")]
    public float? MinValue { get; set; }

    [JsonPropertyName("maxValue")]
    public float? MaxValue { get; set; }

    [JsonPropertyName("step")]
    public float? Step { get; set; }

    // --- Enum-specific properties ---
    // This will be null if the type is not 'enum'.
    [JsonPropertyName("options")]
    public Dictionary<string, string>? Options { get; set; }
}