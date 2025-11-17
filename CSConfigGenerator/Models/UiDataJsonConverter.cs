using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Nodes;

namespace CSConfigGenerator.Models;

public class UiDataJsonConverter : JsonConverter<UiData>
{
    public override UiData? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var jsonObject = JsonNode.Parse(ref reader) ?? throw new JsonException("Failed to parse JSON for UiData.");

        var typeString = jsonObject["type"]?.GetValue<string>() ?? throw new JsonException("Missing 'type' property in UiData.");

        var type = Enum.Parse<SettingType>(typeString, true);

        // Add default ranges for numeric types if not present
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

        return type switch
        {
            SettingType.Bool => JsonSerializer.Deserialize<BoolUiData>(jsonObject.ToJsonString(), options),
            SettingType.Int => JsonSerializer.Deserialize<IntegerUiData>(jsonObject.ToJsonString(), options),
            SettingType.Float => JsonSerializer.Deserialize<FloatUiData>(jsonObject.ToJsonString(), options),
            SettingType.String => JsonSerializer.Deserialize<StringUiData>(jsonObject.ToJsonString(), options),
            SettingType.Enum => JsonSerializer.Deserialize<EnumUiData>(jsonObject.ToJsonString(), options),
            SettingType.Command => JsonSerializer.Deserialize<CommandUiData>(jsonObject.ToJsonString(), options),
            SettingType.Bitmask => JsonSerializer.Deserialize<BitmaskUiData>(jsonObject.ToJsonString(), options),
            SettingType.Unknown => JsonSerializer.Deserialize<UnknownUiData>(jsonObject.ToJsonString(), options),
            SettingType.Color => JsonSerializer.Deserialize<ColorUiData>(jsonObject.ToJsonString(), options),
            SettingType.UInt32 => JsonSerializer.Deserialize<UInt32UiData>(jsonObject.ToJsonString(), options),
            SettingType.UInt64 => JsonSerializer.Deserialize<UInt64UiData>(jsonObject.ToJsonString(), options),
            SettingType.Vector2 => JsonSerializer.Deserialize<Vector2UiData>(jsonObject.ToJsonString(), options),
            SettingType.Vector3 => JsonSerializer.Deserialize<Vector3UiData>(jsonObject.ToJsonString(), options),
            _ => throw new JsonException($"Unknown UiData type: {type}"),
        };
    }

    public override void Write(Utf8JsonWriter writer, UiData value, JsonSerializerOptions options)
    {
        JsonSerializer.Serialize(writer, (object) value, options);
    }
}
