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

    [JsonPropertyName("typeInfo")]
    public required TypeInfo TypeInfo { get; init; }

    // --- Convenience properties that derive values from consoleData/uiData ---

    /// <summary>
    /// Whether this command requires sv_cheats 1. Derived from consoleData.flags.
    /// </summary>
    [JsonIgnore]
    public bool RequiresCheats => ConsoleData.Flags?.Contains("cheat") ?? false;

    /// <summary>
    /// The display description. Prefers typeInfo.description if set, falls back to consoleData.description.
    /// </summary>
    [JsonIgnore]
    public string DisplayDescription => !string.IsNullOrEmpty(TypeInfo.Description)
        ? TypeInfo.Description
        : ConsoleData.Description;

    /// <summary>
    /// The typed default value, parsed from consoleData.defaultValue using the typeInfo type.
    /// Returns null for commands (which have no default value) or if parsing fails.
    /// </summary>
    [JsonIgnore]
    public object? TypedDefaultValue
    {
        get
        {
            if (string.IsNullOrEmpty(ConsoleData.DefaultValue))
                return null;

            try
            {
                return TypeInfo.ParseFromString(ConsoleData.DefaultValue);
            }
            catch
            {
                // If parsing fails, return the type's fallback default
                return TypeInfo.DefaultValue;
            }
        }
    }
}
