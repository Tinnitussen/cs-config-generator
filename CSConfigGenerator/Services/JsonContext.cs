using System.Text.Json;
using System.Text.Json.Serialization;
using CSConfigGenerator.Models;

namespace CSConfigGenerator.Services;

[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    ReadCommentHandling = JsonCommentHandling.Skip,
    AllowTrailingCommas = true)]
[JsonSerializable(typeof(List<string>))]
[JsonSerializable(typeof(List<CommandDefinition>))]
public partial class JsonContext : JsonSerializerContext
{
}