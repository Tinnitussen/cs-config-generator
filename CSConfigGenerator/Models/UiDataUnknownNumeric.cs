using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataUnknownNumeric : UiData
{
    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    public UiDataUnknownNumeric()
    {
        Type = SettingType.UnknownNumeric;
    }

    public override object GetTypedDefaultValue() => DefaultValue.GetSingle();

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (float.TryParse(value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var result))
        {
            parsedValue = result;
            return true;
        }
        parsedValue = null;
        return false;
    }
}
