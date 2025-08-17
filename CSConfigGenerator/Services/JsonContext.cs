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
[JsonSerializable(typeof(ConsoleData))]
[JsonSerializable(typeof(UiData))]
[JsonSerializable(typeof(NumericRange))]
[JsonSerializable(typeof(UiDataAction))]
[JsonSerializable(typeof(UiDataBitmask))]
[JsonSerializable(typeof(UiDataBool))]
[JsonSerializable(typeof(UiDataEnum))]
[JsonSerializable(typeof(UiDataFloat))]
[JsonSerializable(typeof(UiDataInteger))]
[JsonSerializable(typeof(UiDataString))]
[JsonSerializable(typeof(UiDataUnknownInteger))]
[JsonSerializable(typeof(UiDataUnknownNumeric))]
public partial class JsonContext : JsonSerializerContext
{
}
