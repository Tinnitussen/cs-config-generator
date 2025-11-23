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
[JsonSerializable(typeof(CommandUiData))]
[JsonSerializable(typeof(BitmaskUiData))]
[JsonSerializable(typeof(UnknownUiData))]
[JsonSerializable(typeof(NumericRange))]
[JsonSerializable(typeof(UInt32UiData))]
[JsonSerializable(typeof(UInt64UiData))]
[JsonSerializable(typeof(ColorUiData))]
[JsonSerializable(typeof(Vector2UiData))]
[JsonSerializable(typeof(Vector3UiData))]
public partial class JsonContext : JsonSerializerContext
{
}
