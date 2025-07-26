// /Services/SchemaService.cs
using CSConfigGenerator.Models;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CSConfigGenerator.Services;

/// <summary>
/// A singleton service responsible for loading all command schema definitions
/// from the /wwwroot/Data directory on application startup.
/// In a WASM app, this is done via HTTP requests.
/// </summary>
/// <remarks>
/// The service is initialized with an HttpClient to fetch the schema files.
/// </remarks>
public class SchemaService(HttpClient httpClient)
{
    private readonly HttpClient _httpClient = httpClient;
    private readonly List<CommandDefinition> _commands = [];

    /// <summary>
    /// A read-only list of all command definitions loaded from the JSON files.
    /// </summary>
    public IReadOnlyList<CommandDefinition> Commands => _commands.AsReadOnly();

    /// <summary>
    /// Asynchronously loads all schemas. This method must be called explicitly
    /// from Program.cs during application startup.
    /// </summary>
    public async Task InitializeAsync()
    {
        // Configure the JSON serializer to be case-insensitive and to handle enums as strings.
        var jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
        };
        jsonOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.CamelCase));
        
        try
        {
            // First, fetch a manifest file that lists all other schema files.
            // This avoids trying to "list a directory" over HTTP, which isn't possible.
            var manifest = await _httpClient.GetFromJsonAsync<List<string>>("Data/manifest.json", jsonOptions);

            if (manifest is null) return;

            foreach (var filePath in manifest)
            {
                try
                {
                    var commandsInFile = await _httpClient.GetFromJsonAsync<List<CommandDefinition>>(filePath, jsonOptions);
                    if (commandsInFile != null)
                    {
                        _commands.AddRange(commandsInFile);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading schema from {filePath}: {ex.Message}");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to load the schema manifest: {ex.Message}");
        }
    }
}
