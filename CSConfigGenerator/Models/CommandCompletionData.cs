namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

/// <summary>
/// Simplified command data for Monaco editor intellisense.
/// This DTO is serialized to JavaScript for autocomplete/hover support.
/// </summary>
public record CommandCompletionData
{
    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("type")]
    public required string Type { get; init; }

    [JsonPropertyName("description")]
    public string Description { get; init; } = string.Empty;

    [JsonPropertyName("defaultValue")]
    public string? DefaultValue { get; init; }

    [JsonPropertyName("range")]
    public string? Range { get; init; }

    [JsonPropertyName("isCheat")]
    public bool IsCheat { get; init; }

    /// <summary>
    /// Creates a CommandCompletionData from a CommandDefinition.
    /// </summary>
    public static CommandCompletionData FromCommandDefinition(CommandDefinition cmd)
    {
        // Build range string for numeric types
        string? rangeStr = null;
        if (cmd.TypeInfo is IntegerTypeInfo intType)
        {
            rangeStr = FormatRange(intType.Range);
        }
        else if (cmd.TypeInfo is FloatTypeInfo floatType)
        {
            rangeStr = FormatRange(floatType.Range);
        }
        else if (cmd.TypeInfo is Vector3TypeInfo vec3Type)
        {
            rangeStr = FormatRange(vec3Type.Range);
        }

        return new CommandCompletionData
        {
            Command = cmd.Command,
            Type = cmd.TypeInfo.Type.ToString().ToLowerInvariant(),
            Description = cmd.DisplayDescription,
            DefaultValue = cmd.ConsoleData.DefaultValue,
            Range = rangeStr,
            IsCheat = cmd.RequiresCheats
        };
    }

    private static string? FormatRange(NumericRange? range)
    {
        if (range == null)
            return null;

        if (range.MinValue.HasValue && range.MaxValue.HasValue)
            return $"{range.MinValue.Value}–{range.MaxValue.Value}";

        if (range.MinValue.HasValue)
            return $"{range.MinValue.Value}+";

        if (range.MaxValue.HasValue)
            return $"≤{range.MaxValue.Value}";

        return null;
    }
}
