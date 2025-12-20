namespace CSConfigGenerator.Models;

using System;
using System.Globalization;
using System.Text.Json.Serialization;

public record BoolTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Bool;

    [JsonIgnore]
    public override object DefaultValue => false;

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

public record IntegerTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Int;

    [JsonIgnore]
    public override object DefaultValue => 0;

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    public override object ParseFromString(string value) => int.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((int)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToInt32(value);
}

public record FloatTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Float;

    [JsonIgnore]
    public override object DefaultValue => 0f;

    [JsonPropertyName("range")]
    public required NumericRange Range { get; init; }

    public override object ParseFromString(string value) => float.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((float)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToSingle(value);
}

public record ColorTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Color;

    [JsonIgnore]
    public override object DefaultValue => string.Empty;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => $"\"{(string)value}\"";

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record UInt32TypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.UInt32;

    [JsonIgnore]
    public override object DefaultValue => 0u;

    public override object ParseFromString(string value) => uint.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((uint)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToUInt32(value);
}

public record UInt64TypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.UInt64;

    [JsonIgnore]
    public override object DefaultValue => 0ul;

    public override object ParseFromString(string value) => ulong.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((ulong)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToUInt64(value);
}

public record Vector2TypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Vector2;

    [JsonIgnore]
    public override object DefaultValue => "0 0";

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => $"\"{(string)value}\"";

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record Vector3TypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Vector3;

    [JsonIgnore]
    public override object DefaultValue => "0 0 0";

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

public record StringTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.String;

    [JsonIgnore]
    public override object DefaultValue => string.Empty;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value)
    {
        var str = (string)value;
        return (str.Contains(' ') || str.Contains(';')) ? $"\"{str}\"" : str;
    }

    public override object ConvertToType(object? value) => value?.ToString() ?? string.Empty;
}

public record CommandTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Command;

    [JsonIgnore]
    public override object DefaultValue => string.Empty;

    public override object ParseFromString(string value) => value;

    public override string FormatForConfig(object value) => (string)value;

    public override object ConvertToType(object value) => value?.ToString() ?? string.Empty;
}

public record BitmaskTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Bitmask;

    [JsonIgnore]
    public override object DefaultValue => 0;

    [JsonPropertyName("options")]
    public required Dictionary<string, string> Options { get; init; }

    public override object ParseFromString(string value) => int.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((int)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToInt32(value);
}

public record UnknownTypeInfo : TypeInfo
{
    public override SettingType Type => SettingType.Unknown;

    [JsonIgnore]
    public override object DefaultValue => 0f;

    public override object ParseFromString(string value) => float.Parse(value, CultureInfo.InvariantCulture);

    public override string FormatForConfig(object value) => ((float)value).ToString(CultureInfo.InvariantCulture);

    public override object ConvertToType(object value) => Convert.ToSingle(value);
}

