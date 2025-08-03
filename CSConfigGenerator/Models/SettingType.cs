using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Defines the types of settings that can be configured in the application
/// </summary>
public enum SettingType
{
    [RegularExpression("^(true|false|0|1)$", ErrorMessage = "Boolean value must be 'true', 'false', '1', or '0'")]
    Bool,

    [Range(int.MinValue, int.MaxValue, ErrorMessage = "Value must be a valid integer")]
    Int,

    [Range(float.MinValue, float.MaxValue, ErrorMessage = "Value must be a valid floating point number")]
    Float,

    String,
    [Range(int.MinValue, int.MaxValue, ErrorMessage = "Value must be a valid integer")]
    Enum,

    [Range(int.MinValue, int.MaxValue, ErrorMessage = "Value must be a valid integer")]
    Bitmask,

    [Range(float.MinValue, float.MaxValue, ErrorMessage = "Value must be a valid numeric value")]
    UnknownNumeric,

    [Range(int.MinValue, int.MaxValue, ErrorMessage = "Value must be a valid integer")]
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
            SettingType.Enum => element.GetInt32(),
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
    /// <remarks>
    /// This method assumes the input has already been validated with SettingValidator.Validate
    /// </remarks>
    public static object ParseFromString(SettingType settingType, string valueStr)
    {
        return settingType switch
        {
            SettingType.Bool => ParseBooleanValue(valueStr),
            SettingType.Int => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.Float => float.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.String => valueStr,
            SettingType.Enum => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.Bitmask => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.UnknownNumeric => float.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.UnknownInteger => int.Parse(valueStr, CultureInfo.InvariantCulture),
            SettingType.Action => valueStr,
            _ => GetDefaultValue(settingType) // Return default value instead of throwing
        };
    }

    /// <summary>
    /// Parses a string representation of a boolean value, handling "0" and "1" as well as "true" and "false"
    /// </summary>
    private static bool ParseBooleanValue(string valueStr)
    {
        return valueStr switch
        {
            "0" => false,
            "1" => true,
            _ => bool.Parse(valueStr) // This handles "true" and "false" (case-insensitive)
        };
    }

    /// <summary>
    /// Formats a value for output to a config file based on SettingType
    /// </summary>
    public static string FormatForConfig(SettingType settingType, object value)
    {
        return settingType switch
        {
            SettingType.Bool => (bool) value ? "true" : "false",
            SettingType.Float => ((float) value).ToString(CultureInfo.InvariantCulture),
            SettingType.Int => ((int) value).ToString(CultureInfo.InvariantCulture),
            SettingType.String => FormatStringValue((string) value),
            SettingType.Enum => ((int) value).ToString(CultureInfo.InvariantCulture),
            SettingType.Bitmask => ((int) value).ToString(CultureInfo.InvariantCulture),
            SettingType.UnknownNumeric => ((float) value).ToString(CultureInfo.InvariantCulture),
            SettingType.UnknownInteger => ((int) value).ToString(CultureInfo.InvariantCulture),
            SettingType.Action => (string) value,
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
            SettingType.Bool => ConvertToBoolean(value),
            SettingType.Int => Convert.ToInt32(value),
            SettingType.Float => Convert.ToSingle(value),
            SettingType.String => value.ToString() ?? string.Empty,
            SettingType.Enum => Convert.ToInt32(value),
            SettingType.Bitmask => Convert.ToInt32(value),
            SettingType.UnknownNumeric => Convert.ToSingle(value),
            SettingType.UnknownInteger => Convert.ToInt32(value),
            SettingType.Action => value.ToString() ?? string.Empty,
            _ => throw new ArgumentException($"Unsupported setting type: {settingType}")
        };
    }

    /// <summary>
    /// Converts an object to a boolean, handling integer values (0, 1) as well as standard boolean conversion
    /// </summary>
    private static bool ConvertToBoolean(object value)
    {
        if (value is int intValue)
        {
            return intValue != 0;
        }

        if (value is string strValue)
        {
            return ParseBooleanValue(strValue);
        }

        return Convert.ToBoolean(value);
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
            SettingType.Enum => 0,
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
