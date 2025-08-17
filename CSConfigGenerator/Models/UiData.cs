using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
[JsonDerivedType(typeof(UiDataBool), typeDiscriminator: "bool")]
[JsonDerivedType(typeof(UiDataInteger), typeDiscriminator: "integer")]
[JsonDerivedType(typeof(UiDataFloat), typeDiscriminator: "float")]
[JsonDerivedType(typeof(UiDataString), typeDiscriminator: "string")]
[JsonDerivedType(typeof(UiDataEnum), typeDiscriminator: "enum")]
[JsonDerivedType(typeof(UiDataAction), typeDiscriminator: "action")]
[JsonDerivedType(typeof(UiDataBitmask), typeDiscriminator: "bitmask")]
[JsonDerivedType(typeof(UiDataUnknownNumeric), typeDiscriminator: "unknown_numeric")]
[JsonDerivedType(typeof(UiDataUnknownInteger), typeDiscriminator: "unknown_integer")]
public abstract record UiData
{
    [JsonPropertyName("label")]
    public required string Label { get; init; }

    [JsonPropertyName("helperText")]
    public string HelperText { get; init; } = string.Empty;

    [JsonPropertyName("requiresCheats")]
    public bool RequiresCheats { get; init; }

    [JsonPropertyName("aliasFor")]
    public string? AliasFor { get; init; }

    [JsonPropertyName("deprecated")]
    public bool Deprecated { get; init; }

    [JsonIgnore]
    public SettingType Type { get; protected set; }

    public abstract bool TryParse(string value, out object? parsedValue);
    public abstract object GetTypedDefaultValue();
}

public record VisibilityCondition
{
    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("value")]
    public required object Value { get; init; }
}
