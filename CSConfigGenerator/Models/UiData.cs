namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

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
