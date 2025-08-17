using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record Argument
{
    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("label")]
    public required string Label { get; init; }

    [JsonPropertyName("type")]
    public required string Type { get; init; }

    [JsonPropertyName("placeholder")]
    public string? Placeholder { get; init; }

    [JsonPropertyName("required")]
    public bool Required { get; init; }
}
