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
[JsonSerializable(typeof(TypeInfo))]
[JsonSerializable(typeof(BoolTypeInfo))]
[JsonSerializable(typeof(IntegerTypeInfo))]
[JsonSerializable(typeof(FloatTypeInfo))]
[JsonSerializable(typeof(StringTypeInfo))]
[JsonSerializable(typeof(CommandTypeInfo))]
[JsonSerializable(typeof(BitmaskTypeInfo))]
[JsonSerializable(typeof(UnknownTypeInfo))]
[JsonSerializable(typeof(NumericRange))]
[JsonSerializable(typeof(UInt32TypeInfo))]
[JsonSerializable(typeof(UInt64TypeInfo))]
[JsonSerializable(typeof(ColorTypeInfo))]
[JsonSerializable(typeof(Vector2TypeInfo))]
[JsonSerializable(typeof(Vector3TypeInfo))]
public partial class JsonContext : JsonSerializerContext
{
}
