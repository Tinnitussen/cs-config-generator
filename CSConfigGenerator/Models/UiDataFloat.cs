using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataFloat : UiData
{
    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    [JsonPropertyName("visibilityCondition")]
    public VisibilityCondition? VisibilityCondition { get; init; }

    public UiDataFloat()
    {
        Type = SettingType.Float;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (float.TryParse(value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var result))
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

    public override object GetTypedDefaultValue() => DefaultValue.GetSingle();
}
