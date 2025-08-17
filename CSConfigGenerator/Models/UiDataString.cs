using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataString : UiData
{
    [JsonPropertyName("defaultValue")]
    public required string DefaultValue { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataString()
    {
        Type = SettingType.String;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        parsedValue = value;
        return true;
    }
}
