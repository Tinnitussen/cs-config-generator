namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

public record BoolUiData : UiData
{
    public override SettingType Type => SettingType.Bool;

    [JsonPropertyName("defaultValue")]
    public bool DefaultValue { get; init; }
}

public record IntegerUiData : UiData
{
    public override SettingType Type => SettingType.Integer;

    [JsonPropertyName("defaultValue")]
    public int DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }
}

public record FloatUiData : UiData
{
    public override SettingType Type => SettingType.Float;

    [JsonPropertyName("defaultValue")]
    public float DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }
}

public record StringUiData : UiData
{
    public override SettingType Type => SettingType.String;

    [JsonPropertyName("defaultValue")]
    public required string DefaultValue { get; init; }
}

public record EnumUiData : UiData
{
    public override SettingType Type => SettingType.Enum;

    [JsonPropertyName("defaultValue")]
    public required string DefaultValue { get; init; }

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }
}

public record ActionUiData : UiData
{
    public override SettingType Type => SettingType.Action;
}

public record BitmaskUiData : UiData
{
    public override SettingType Type => SettingType.Bitmask;

    [JsonPropertyName("defaultValue")]
    public int DefaultValue { get; init; }

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }
}

public record UnknownUiData : UiData
{
    public override SettingType Type => SettingType.Unknown;

    [JsonPropertyName("defaultValue")]
    public required string DefaultValue { get; init; }
}
