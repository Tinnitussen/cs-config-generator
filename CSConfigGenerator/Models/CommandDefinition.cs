using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Represents the complete definition for a single console variable (cvar).
/// This class is designed to be deserialized from your JSON schema files.
/// </summary>
public record CommandDefinition
{
    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("consoleData")]
    public required ConsoleData ConsoleData { get; init; }

    [JsonPropertyName("uiData")]
    public required UiData UiData { get; init; }
}