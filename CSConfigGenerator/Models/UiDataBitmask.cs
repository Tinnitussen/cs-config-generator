using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataBitmask : UiData
{
    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataBitmask()
    {
        Type = SettingType.Bitmask;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (int.TryParse(value, out var result))
        {
            parsedValue = result;
            return true;
        }
        parsedValue = null;
        return false;
    }

    public override object GetTypedDefaultValue() => DefaultValue.GetInt32();
}
