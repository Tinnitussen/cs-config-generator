using System.Net;
using System.Net.Http;
using CSConfigGenerator.Interfaces;
using CSConfigGenerator.Models;
using CSConfigGenerator.Services;
using Xunit;

namespace CSConfigGenerator.Tests;

public class SchemaServiceTests
{
    private class MockHttpMessageHandler : HttpMessageHandler
    {
        private readonly Dictionary<string, string> _responses = new();
        public void AddJson(string url, string json) => _responses[url] = json;
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var path = request.RequestUri!.ToString();
            if (_responses.TryGetValue(path, out var json))
            {
                return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(json)
                });
            }
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound));
        }
    }

    [Fact]
    public async Task InitializeAsync_LoadsCommandsAndLookupWorks()
    {
        var handler = new MockHttpMessageHandler();
        handler.AddJson("http://localhost/data/manifest.json", "[\"data/commandschema/all_commands.json\"]");
        handler.AddJson("http://localhost/data/commandschema/all_commands.json", 
            """[{"command": "test_command", "consoleData": {"defaultValue": null}, "typeInfo": {"type": "command"}}]""");

        var httpClient = new HttpClient(handler) { BaseAddress = new Uri("http://localhost") };
        ISchemaService schemaService = new SchemaService(httpClient);

        await schemaService.InitializeAsync();

        Assert.NotEmpty(schemaService.Commands);
        var lookup = schemaService.GetCommand("test_command");
        Assert.NotNull(lookup);
        Assert.Equal("test_command", lookup!.Command);
        Assert.Equal(SettingType.Command, lookup.TypeInfo.Type);
    }

    [Fact]
    public async Task InitializeAsync_LoadsIntegerCommand()
    {
        var handler = new MockHttpMessageHandler();
        handler.AddJson("http://localhost/data/manifest.json", "[\"data/commandschema/all_commands.json\"]");
        handler.AddJson("http://localhost/data/commandschema/all_commands.json", 
            """[{"command": "int_test", "consoleData": {"defaultValue": "5"}, "typeInfo": {"type": "int", "range": {"minValue": 0, "maxValue": 20}}}]""");

        var httpClient = new HttpClient(handler) { BaseAddress = new Uri("http://localhost") };
        ISchemaService schemaService = new SchemaService(httpClient);
        await schemaService.InitializeAsync();

        var lookup = schemaService.GetCommand("int_test");
        Assert.NotNull(lookup);
        Assert.Equal(SettingType.Int, lookup!.TypeInfo.Type);
        // TypedDefaultValue parses consoleData.defaultValue using the type
        Assert.Equal(5, lookup.TypedDefaultValue);
    }

    [Fact]
    public void Deserialize_Command_With_Null_DefaultValue_Should_Work()
    {
        const string json = """[{"command": "+cl_show_team_equipment", "consoleData": {"defaultValue": null}, "typeInfo": {"type": "command"}}]""";
        var options = new System.Text.Json.JsonSerializerOptions(System.Text.Json.JsonSerializerDefaults.Web)
        {
            TypeInfoResolver = JsonContext.Default
        };
        var list = System.Text.Json.JsonSerializer.Deserialize<List<CommandDefinition>>(json, options);
        Assert.NotNull(list);
        Assert.Single(list);
        Assert.Equal("+cl_show_team_equipment", list![0].Command);
        Assert.Equal(SettingType.Command, list[0].TypeInfo.Type);
        Assert.Null(list[0].TypedDefaultValue); // Commands have null default
    }

    [Fact]
    public void Deserialize_Unknown_With_Numeric_DefaultValue_Should_Work()
    {
        const string json = """[{"command": "unknown_numeric", "consoleData": {"defaultValue": "12.5"}, "typeInfo": {"type": "unknown"}}]""";
        var options = new System.Text.Json.JsonSerializerOptions(System.Text.Json.JsonSerializerDefaults.Web)
        {
            TypeInfoResolver = JsonContext.Default
        };
        var list = System.Text.Json.JsonSerializer.Deserialize<List<CommandDefinition>>(json, options);
        Assert.NotNull(list);
        Assert.Single(list);
        Assert.Equal(SettingType.Unknown, list![0].TypeInfo.Type);
        // TypedDefaultValue parses consoleData.defaultValue
        Assert.Equal(12.5f, list[0].TypedDefaultValue);
    }
}
