namespace CSConfigGenerator.Models;

using System.Text.Json;
using System.Text.Json.Serialization;

public record UiData
{
    [JsonPropertyName("label")]
    public required string Label { get; init; }

    [JsonPropertyName("helperText")]
    public string HelperText { get; init; } = string.Empty;

    [JsonPropertyName("type")]
    [JsonConverter(typeof(SettingTypeJsonConverter))]
    public required SettingType Type { get; init; }

    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    [JsonPropertyName("requiresCheats")]
    public bool RequiresCheats { get; init; }

    [JsonPropertyName("range")]
    public NumericRange? Range { get; init; }

    [JsonPropertyName("options")]
    public Dictionary<string, string>? Options { get; init; }
}
