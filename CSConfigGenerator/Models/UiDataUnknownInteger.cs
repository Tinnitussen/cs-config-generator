using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataUnknownInteger : UiData
{
    [JsonPropertyName("defaultValue")]
    public required JsonElement DefaultValue { get; init; }

    public UiDataUnknownInteger()
    {
        Type = SettingType.UnknownInteger;
    }

    public override object GetTypedDefaultValue() => DefaultValue.GetInt32();

    public override bool TryParse(string value, out object? parsedValue)
    {
        if (int.TryParse(value, System.Globalization.NumberStyles.Integer, System.Globalization.CultureInfo.InvariantCulture, out var result))
        {
            parsedValue = result;
            return true;
        }
        parsedValue = null;
        return false;
    }
}
