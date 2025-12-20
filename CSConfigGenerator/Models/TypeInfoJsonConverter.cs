using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Nodes;

namespace CSConfigGenerator.Models;

public class TypeInfoJsonConverter : JsonConverter<TypeInfo>
{
    public override TypeInfo? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var jsonObject = JsonNode.Parse(ref reader) ?? throw new JsonException("Failed to parse JSON for TypeInfo.");

        var typeString = jsonObject["type"]?.GetValue<string>() ?? throw new JsonException("Missing 'type' property in TypeInfo.");

        var type = Enum.Parse<SettingType>(typeString, true);

        // Add default ranges for numeric / range-required types if not present
        if (type == SettingType.Int && jsonObject["range"] is null)
        {
            jsonObject["range"] = JsonNode.Parse("""
                {
                    "minValue": 0,
                    "maxValue": 100,
                    "step": 1
                }
                """);
        }
        else if (type == SettingType.Float && jsonObject["range"] is null)
        {
            jsonObject["range"] = JsonNode.Parse("""
                {
                    "minValue": 0.0,
                    "maxValue": 1.0,
                    "step": 0.01
                }
                """);
        }
        else if (type == SettingType.Vector3 && jsonObject["range"] is null)
        {
            // Vector3 requires a range object; provide a permissive default with null bounds
            jsonObject["range"] = JsonNode.Parse("""
                {
                    "minValue": null,
                    "maxValue": null,
                    "step": null
                }
                """);
        }

        return type switch
        {
            SettingType.Bool => JsonSerializer.Deserialize<BoolTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Int => JsonSerializer.Deserialize<IntegerTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Float => JsonSerializer.Deserialize<FloatTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.String => JsonSerializer.Deserialize<StringTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Command => JsonSerializer.Deserialize<CommandTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Bitmask => JsonSerializer.Deserialize<BitmaskTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Unknown => JsonSerializer.Deserialize<UnknownTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Color => JsonSerializer.Deserialize<ColorTypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.UInt32 => JsonSerializer.Deserialize<UInt32TypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.UInt64 => JsonSerializer.Deserialize<UInt64TypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Vector2 => JsonSerializer.Deserialize<Vector2TypeInfo>(jsonObject.ToJsonString(), options),
            SettingType.Vector3 => JsonSerializer.Deserialize<Vector3TypeInfo>(jsonObject.ToJsonString(), options),
            _ => throw new JsonException($"Unknown TypeInfo type: {type}"),
        };
    }

    public override void Write(Utf8JsonWriter writer, TypeInfo value, JsonSerializerOptions options)
    {
        JsonSerializer.Serialize(writer, (object) value, options);
    }
}

