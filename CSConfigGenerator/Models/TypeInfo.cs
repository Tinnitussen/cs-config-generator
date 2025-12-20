namespace CSConfigGenerator.Models;

using System.Text.Json.Serialization;

[JsonConverter(typeof(TypeInfoJsonConverter))]
public abstract record TypeInfo
{
    /// <summary>
    /// Optional custom description. If null/empty, use ConsoleData.Description instead.
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; init; }

    [JsonPropertyName("type")]
    public abstract SettingType Type { get; }

    /// <summary>
    /// Returns the typed default value. Concrete types may return a parsed version
    /// of ConsoleData.DefaultValue or a type-specific default.
    /// </summary>
    [JsonIgnore]
    public abstract object DefaultValue { get; }

    public abstract object ParseFromString(string value);

    public abstract string FormatForConfig(object value);

    public abstract object ConvertToType(object value);
}

