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

public record ColorUiData : UiData
{
    public override SettingType Type => SettingType.Color;

    [JsonPropertyName("defaultValue")]
    public required string RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => $"\"{(string)value}\"";

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record UInt32UiData : UiData
{
    public override SettingType Type => SettingType.UInt32;

    [JsonPropertyName("defaultValue")]
    public uint RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => uint.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((uint)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToUInt32(value);
}

public record UInt64UiData : UiData
{
    public override SettingType Type => SettingType.UInt64;

    [JsonPropertyName("defaultValue")]
    public ulong RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => ulong.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((ulong)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToUInt64(value);
}

public record Vector2UiData : UiData
{
    public override SettingType Type => SettingType.Vector2;

    [JsonPropertyName("defaultValue")]
    public required string RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => $"\"{(string)value}\"";

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record Vector3UiData : UiData
{
    public override SettingType Type => SettingType.Vector3;

    [JsonPropertyName("defaultValue")]
    public required string RawDefaultValue { get; init; }

    [JsonIgnore]
    public override object DefaultValue => RawDefaultValue;

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    // Helper to parse a vector string "x y z" into a float array
    private static float[] ParseVector3(string value)
    {
        var parts = value.Split(' ');
        if (parts.Length != 3)
            throw new FormatException("Vector3 value must have three components separated by spaces.");
        return new float[]
        {
            float.Parse(parts[0], CultureInfo.InvariantCulture),
            float.Parse(parts[1], CultureInfo.InvariantCulture),
            float.Parse(parts[2], CultureInfo.InvariantCulture)
        };
    }

    // Helper to validate vector components against the range
    private void ValidateVectorRange(float[] vector)
    {
        if (Range.MinValue.HasValue || Range.MaxValue.HasValue)
        {
            for (int i = 0; i < vector.Length; i++)
            {
                if (Range.MinValue.HasValue && vector[i] < Range.MinValue.Value)
                {
                    throw new ArgumentOutOfRangeException(nameof(vector),
                        $"Vector3 component {i} ({vector[i]}) is below minimum value {Range.MinValue.Value}.");
                }
                if (Range.MaxValue.HasValue && vector[i] > Range.MaxValue.Value)
                {
                    throw new ArgumentOutOfRangeException(nameof(vector),
                        $"Vector3 component {i} ({vector[i]}) is above maximum value {Range.MaxValue.Value}.");
                }
            }
        }
    }

    public override object ParseFromString(string value)
    {
        var vector = ParseVector3(value);
        ValidateVectorRange(vector);
        return value;
    }

    public override string FormatForConfig(object value) => $"\"{(string)value}\"";

    public override object ConvertToType(object? value)
    {
        var str = value?.ToString() ?? string.Empty;
        var vector = ParseVector3(str);
        ValidateVectorRange(vector);
        return str;
    }
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

public record CommandUiData : UiData
{
    public override SettingType Type => SettingType.Command;

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
