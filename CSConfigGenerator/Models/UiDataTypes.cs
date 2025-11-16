namespace CSConfigGenerator.Models;

using System;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

public record BoolUiData : UiData
{
    public override SettingType Type => SettingType.Bool;

    [JsonPropertyName("defaultValue")]
    public bool RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => value switch
    {
        "0" => false,
        "1" => true,
        _ => bool.Parse(value)
    };

    public override string FormatForConfig(object value) => (bool)value ? "true" : "false";

    public override object ConvertToType(object value)
    {
        if (value is int i) return i != 0;
        if (value is string s) return ParseFromString(s);
        return Convert.ToBoolean(value);
    }
}

public record IntegerUiData : UiData
{
    public override SettingType Type => SettingType.Int;

    [JsonPropertyName("defaultValue")]
    public int RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    public override object ParseFromString(string value) => int.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((int)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToInt32(value);
}

public record FloatUiData : UiData
{
    public override SettingType Type => SettingType.Float;

    [JsonPropertyName("defaultValue")]
    public float RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    public override object ParseFromString(string value) => float.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((float)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToSingle(value);
}

public record StringUiData : UiData
{
    public override SettingType Type => SettingType.String;

    [JsonPropertyName("defaultValue")]
    public required string RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value)
    {
        var str = (string)value;
        return (str.Contains(' ') || str.Contains(';')) ? $"\"{str}\"" : str;
    }

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record EnumUiData : UiData
{
    public override SettingType Type => SettingType.Enum;

    [JsonPropertyName("defaultValue")]
    public required string RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => int.Parse(RawDefaultValue, CultureInfo.InvariantCulture);

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }

    public override object ParseFromString(string value) => int.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((int)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToInt32(value);
}

public record ActionUiData : UiData
{
    public override SettingType Type => SettingType.Action;

    [JsonIgnore]
    public override object DefaultValue => string.Empty;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => (string)value;

    public override object ConvertToType(object value) => value?.ToString() ?? string.Empty;
}

public record BitmaskUiData : UiData
{
    public override SettingType Type => SettingType.Bitmask;

    [JsonPropertyName("defaultValue")]
    public int RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }

    public override object ParseFromString(string value) => int.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((int)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToInt32(value);
}

public record UnknownUiData : UiData
{
    public override SettingType Type => SettingType.Unknown;

    [JsonPropertyName("defaultValue")]
    public JsonElement RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue.ValueKind switch
    {
        JsonValueKind.Number => (float)RawDefaultValue.GetDouble(),
        JsonValueKind.String => float.TryParse(RawDefaultValue.GetString(), NumberStyles.Float, CultureInfo.InvariantCulture, out var f) ? f : 0f,
        _ => 0f
    };

    public override object ParseFromString(string value) => float.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((float)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToSingle(value);
}
