using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataEnum : UiData
{
    [JsonPropertyName("defaultValue")]
    public required int DefaultValue { get; init; }

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataEnum()
    {
        Type = SettingType.Enum;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (int.TryParse(value, out var result))
        {
            if (Options.ContainsKey(result.ToString()))
            {
                parsedValue = result;
                return true;
            }
        }
        parsedValue = null;
        return false;
    }
}
