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
[JsonSerializable(typeof(BoolUiData))]
[JsonSerializable(typeof(IntegerUiData))]
[JsonSerializable(typeof(FloatUiData))]
[JsonSerializable(typeof(StringUiData))]
[JsonSerializable(typeof(EnumUiData))]
[JsonSerializable(typeof(CommandUiData))]
[JsonSerializable(typeof(BitmaskUiData))]
[JsonSerializable(typeof(UnknownUiData))]
[JsonSerializable(typeof(NumericRange))]
public partial class JsonContext : JsonSerializerContext
{
}
