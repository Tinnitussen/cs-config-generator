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
    Bitmask,

    [Range(float.MinValue, float.MaxValue, ErrorMessage = "Value must be a valid numeric value")]
    Unknown,

    Command,
    Color,
    UInt32,
    UInt64,
    Vector2,
    Vector3,
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
            "bitmask" => SettingType.Bitmask,
            "unknown" => SettingType.Unknown,
            "command" => SettingType.Command,
            "color" => SettingType.Color,
            "uint32" => SettingType.UInt32,
            "uint64" => SettingType.UInt64,
            "vector2" => SettingType.Vector2,
            "vector3" => SettingType.Vector3,
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
            SettingType.Bitmask => "bitmask",
            SettingType.Unknown => "unknown",
            SettingType.Command => "command",
            SettingType.Color => "color",
            SettingType.UInt32 => "uint32",
            SettingType.UInt64 => "uint64",
            SettingType.Vector2 => "vector2",
            SettingType.Vector3 => "vector3",
            _ => throw new ArgumentException($"Unknown setting type: {value}")
        };
        writer.WriteStringValue(stringValue);
    }
}
