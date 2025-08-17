using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Represents a condition for a setting's visibility, based on the value of another setting.
/// </summary>
public record VisibilityCondition
{
    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("value")]
    public required object Value { get; init; }
}
