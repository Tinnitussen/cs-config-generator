using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public record UiDataAction : UiData
{
    [JsonPropertyName("defaultValue")]
    public object? DefaultValue { get; init; }

    [JsonPropertyName("arguments")]
    public List<Argument>? Arguments { get; init; }

    public UiDataAction()
    {
        Type = SettingType.Action;
    }

    public override bool TryParse(string value, out object? parsedValue)
    {
        // Actions are commands, not settings with a parsable value in the typical sense.
        // We will consider the "value" as the arguments string.
        parsedValue = value;
        return true;
    }
}
