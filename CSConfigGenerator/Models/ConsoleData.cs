namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

public record ConsoleData
{
    [JsonPropertyName("defaultValue")]
    public string? DefaultValue { get; init; }

    [JsonPropertyName("flags")]
    public List<string>? Flags { get; init; }

    [JsonPropertyName("description")]
    public string Description { get; init; } = string.Empty;

    [JsonPropertyName("sourcedAt")]
    public DateTimeOffset? SourcedAt { get; init; }
}
