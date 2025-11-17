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
        handler.AddJson("http://localhost/data/manifest.json", "[\n  \"data/commandschema/all_commands.json\"\n]");
        // Use command type to avoid defaultValue property collision in serialization
        handler.AddJson("http://localhost/data/commandschema/all_commands.json", "[ { \n  \"command\": \"test_command\", \n  \"consoleData\": { \"defaultValue\": \"1\" }, \n  \"uiData\": { \n    \"label\": \"Test Command\", \n    \"helperText\": \"A test command\", \n    \"type\": \"command\", \n    \"requiresCheats\": false \n  } \n} ]");

        var httpClient = new HttpClient(handler) { BaseAddress = new Uri("http://localhost") };
        ISchemaService schemaService = new SchemaService(httpClient);

        await schemaService.InitializeAsync();

        Assert.NotEmpty(schemaService.Commands);
        var lookup = schemaService.GetCommand("test_command");
        Assert.NotNull(lookup);
        Assert.Equal("test_command", lookup!.Command);
        Assert.Equal(string.Empty, lookup.UiData.DefaultValue);
    }

    [Fact]
    public async Task InitializeAsync_LoadsIntegerCommand()
    {
        var handler = new MockHttpMessageHandler();
        handler.AddJson("http://localhost/data/manifest.json", "[\n  \"data/commandschema/all_commands.json\"\n]");
        handler.AddJson("http://localhost/data/commandschema/all_commands.json", "[ { \n  \"command\": \"int_test\", \n  \"consoleData\": { \"defaultValue\": \"0\" }, \n  \"uiData\": { \n    \"label\": \"Integer Test\", \n    \"helperText\": \"An integer command\", \n    \"type\": \"int\", \n    \"requiresCheats\": false, \n    \"defaultValue\": 5, \n    \"range\": { \"min\": 0, \"max\": 20 } \n  } \n} ]");

        var httpClient = new HttpClient(handler) { BaseAddress = new Uri("http://localhost") };
        ISchemaService schemaService = new SchemaService(httpClient);
        await schemaService.InitializeAsync();

        var lookup = schemaService.GetCommand("int_test");
        Assert.NotNull(lookup);
        Assert.Equal(5, lookup!.UiData.DefaultValue);
    }

    [Fact]
    public void Deserialize_Command_With_Null_DefaultValue_Should_Work()
    {
        const string json = "[ { \n  \"command\": \"+cl_show_team_equipment\", \n  \"consoleData\": { \"defaultValue\": \"\" }, \n  \"uiData\": { \n    \"label\": \"+cl_show_team_equipment\", \n    \"helperText\": \"Sample command\", \n    \"type\": \"command\", \n    \"requiresCheats\": false, \n    \"defaultValue\": null \n  } \n} ]";
        var options = new System.Text.Json.JsonSerializerOptions(System.Text.Json.JsonSerializerDefaults.Web)
        {
            TypeInfoResolver = JsonContext.Default
        };
        var list = System.Text.Json.JsonSerializer.Deserialize<List<CommandDefinition>>(json, options);
        Assert.NotNull(list);
        Assert.Single(list);
        Assert.Equal("+cl_show_team_equipment", list![0].Command);
        Assert.Equal(string.Empty, list[0].UiData.DefaultValue);
    }

    [Fact]
    public void Deserialize_Unknown_With_Numeric_DefaultValue_Should_Work()
    {
        const string json = "[ { \n  \"command\": \"unknown_numeric\", \n  \"consoleData\": { \"defaultValue\": \"0\" }, \n  \"uiData\": { \n    \"label\": \"Unknown Numeric\", \n    \"helperText\": \"An unknown numeric value\", \n    \"type\": \"unknown\", \n    \"requiresCheats\": false, \n    \"defaultValue\": 12.5 \n  } \n} ]";
        var options = new System.Text.Json.JsonSerializerOptions(System.Text.Json.JsonSerializerDefaults.Web)
        {
            TypeInfoResolver = JsonContext.Default
        };
        var list = System.Text.Json.JsonSerializer.Deserialize<List<CommandDefinition>>(json, options);
        Assert.NotNull(list);
        Assert.Single(list);
        Assert.Equal(12.5f, (float)list![0].UiData.DefaultValue);
    }
}
