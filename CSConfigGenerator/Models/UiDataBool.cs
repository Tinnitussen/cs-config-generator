using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataBool : UiData
{
    [JsonPropertyName("defaultValue")]
    public required bool DefaultValue { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataBool()
    {
        Type = SettingType.Bool;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (bool.TryParse(value, out var result))
        {
            parsedValue = result;
            return true;
        }
        if (value == "1")
        {
            parsedValue = true;
            return true;
        }
        if (value == "0")
        {
            parsedValue = false;
            return true;
        }
        parsedValue = null;
        return false;
    }
}
