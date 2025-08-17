using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataInteger : UiData
{
    [JsonPropertyName("defaultValue")]
    public required int DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataInteger()
    {
        Type = SettingType.Int;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (int.TryParse(value, System.Globalization.NumberStyles.Integer, System.Globalization.CultureInfo.InvariantCulture, out var result))
        {
            if (result >= Range.MinValue && result <= Range.MaxValue)
            {
                parsedValue = result;
                return true;
            }
        }
        parsedValue = null;
        return false;
    }
}
