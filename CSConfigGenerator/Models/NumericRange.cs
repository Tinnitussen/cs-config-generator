namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

public record NumericRange
{
    [JsonPropertyName("minValue")]
    public float? MinValue { get; init; }

    [JsonPropertyName("maxValue")]
    public float? MaxValue { get; init; }

    [JsonPropertyName("step")]
    public float? Step { get; init; }
}