using System.Text.Json.Serialization;

namespace CSConfigGenerator.Models;

/// <summary>
/// Represents the complete definition for a single console variable (cvar).
/// This class is designed to be deserialized from your JSON schema files.
/// </summary>
public record CommandDefinition
{
    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("consoleData")]
    public required ConsoleData ConsoleData { get; init; }

    [JsonPropertyName("uiData")]
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
    public required UiData UiData { get; init; }
}
