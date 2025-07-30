using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

public enum SettingType
{
    Bool,
    Int,
    Float,
    String,
    Enum,
    Bitmask,
    UnknownNumeric,
    UnknownInteger,
    Action
}

public static class SettingTypeHelpers
{
    /// <summary>
    /// Converts a JsonElement to the appropriate .NET type based on SettingType
    /// </summary>
    public static object ConvertFromJson(SettingType settingType, JsonElement element)
    {
        return settingType switch
        {
            SettingType.Bool => element.GetBoolean(),
            SettingType.Int => element.GetInt32(),
            SettingType.Float => element.GetSingle(),
            SettingType.String => element.GetString() ?? string.Empty,
            SettingType.Enum => element.GetString() ?? string.Empty,
            SettingType.Bitmask => element.GetInt32(),
            SettingType.UnknownNumeric => element.GetSingle(),
            SettingType.UnknownInteger => element.GetInt32(),
            SettingType.Action => element.GetString() ?? string.Empty,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    /// <summary>
    /// Converts a string value to the appropriate .NET type based on SettingType
    /// </summary>
    public static object ParseFromString(SettingType settingType, string valueStr)
    {
        return settingType switch
        {
            SettingType.Bool => valueStr is "1" or "true",
            SettingType.Int => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.Float => float.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.String => valueStr,
            SettingType.Enum => valueStr,
            SettingType.Bitmask => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.UnknownNumeric => float.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.UnknownInteger => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.Action => valueStr,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    /// <summary>
    /// Formats a value for output to a config file based on SettingType
    /// </summary>
    public static string FormatForConfig(SettingType settingType, object value)
    {
        return settingType switch
        {
            SettingType.Bool => (bool)value ? "true" : "false",
            SettingType.Float => ((float)value).ToString(CultureInfo.InvariantCulture),
            SettingType.Int => ((int)value).ToString(CultureInfo.InvariantCulture),
            SettingType.String => FormatStringValue((string)value),
            SettingType.Enum => FormatStringValue((string)value),
            SettingType.Bitmask => ((int)value).ToString(CultureInfo.InvariantCulture),
            SettingType.UnknownNumeric => ((float)value).ToString(CultureInfo.InvariantCulture),
            SettingType.UnknownInteger => ((int)value).ToString(CultureInfo.InvariantCulture),
            SettingType.Action => (string)value,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    /// <summary>
    /// Converts any object to the appropriate .NET type based on SettingType
    /// </summary>
    public static object ConvertToType(SettingType settingType, object value)
    {
        return settingType switch
        {
            SettingType.Bool => Convert.ToBoolean(value),
            SettingType.Int => Convert.ToInt32(value),
            SettingType.Float => Convert.ToSingle(value),
            SettingType.String => value.ToString() ?? string.Empty,
            SettingType.Enum => value.ToString() ?? string.Empty,
            SettingType.Bitmask => Convert.ToInt32(value),
            SettingType.UnknownNumeric => Convert.ToSingle(value),
            SettingType.UnknownInteger => Convert.ToInt32(value),
            SettingType.Action => value.ToString() ?? string.Empty,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    /// <summary>
    /// Gets the default value for a SettingType
    /// </summary>
    public static object GetDefaultValue(SettingType settingType)
    {
        return settingType switch
        {
            SettingType.Bool => false,
            SettingType.Int => 0,
            SettingType.Float => 0.0f,
            SettingType.String => string.Empty,
            SettingType.Enum => string.Empty,
            SettingType.Bitmask => 0,
            SettingType.UnknownNumeric => 0.0f,
            SettingType.UnknownInteger => 0,
            SettingType.Action => string.Empty,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    private static string FormatStringValue(string value)
    {
        if (value.Contains(' ') || value.Contains(';'))
        {
            return $"\"{value}\"";
        }
        return value;
    }
}

/// <summary>
/// Custom JSON converter for SettingType to handle string-based JSON values
/// </summary>
public class SettingTypeJsonConverter : JsonConverter<SettingType>
{
    public override SettingType Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var value = reader.GetString();
        return value?.ToLowerInvariant() switch
        {
            "bool" => SettingType.Bool,
            "int" => SettingType.Int,
            "float" => SettingType.Float,
            "string" => SettingType.String,
            "enum" => SettingType.Enum,
            "bitmask" => SettingType.Bitmask,
            "unknown_numeric" => SettingType.UnknownNumeric,
            "unknown_integer" => SettingType.UnknownInteger,
            "action" => SettingType.Action,
            _ => throw new JsonException($"Unknown setting type: {value}")
        };
    }

    public override void Write(Utf8JsonWriter writer, SettingType value, JsonSerializerOptions options)
    {
        var stringValue = value switch
        {
            SettingType.Bool => "bool",
            SettingType.Int => "int",
            SettingType.Float => "float",
            SettingType.String => "string",
            SettingType.Enum => "enum",
            SettingType.Bitmask => "bitmask",
            SettingType.UnknownNumeric => "unknown_numeric",
            SettingType.UnknownInteger => "unknown_integer",
            SettingType.Action => "action",
            _ => throw new ArgumentException($"Unknown setting type: {value}")
        };
        writer.WriteStringValue(stringValue);
    }
}