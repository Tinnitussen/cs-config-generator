using System.Net.Http.Json;
using CSConfigGenerator.Models;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class SchemaService(HttpClient httpClient) : ISchemaService
{
    private readonly HttpClient _httpClient = httpClient;
    private readonly List<ConfigSection> _playerSections = [];
    private readonly List<ConfigSection> _serverSections = [];
    private readonly List<ConfigSection> _allSections = [];
    private readonly Dictionary<string, CommandDefinition> _allCommands = [];
    public IReadOnlyList<ConfigSection> PlayerSections => _playerSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> ServerSections => _serverSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> AllSections => _allSections.AsReadOnly();
    public async Task InitializeAsync()
    {
        try
        {
            var manifest = await _httpClient.GetFromJsonAsync("data/manifest.json", JsonContext.Default.ListString)
                ?? throw new InvalidOperationException("Manifest file could not be loaded or is empty.");

            foreach (var filePath in manifest)
            {
                var commands = await _httpClient.GetFromJsonAsync(filePath, JsonContext.Default.ListCommandDefinition);
                var commandList = (commands ?? []).AsReadOnly();

                var sectionName = ExtractSectionName(filePath);
                var section = new ConfigSection
                {
                    Name = sectionName,
                    DisplayName = FormatDisplayName(sectionName),
                    Commands = commandList
                };

                if (filePath.Contains("/player/"))
                {
                    _playerSections.Add(section);
                }
                else if (filePath.Contains("/server/"))
                {
                    _serverSections.Add(section);
                }
                else if (filePath.Contains("/all/"))
                {
                    _allSections.Add(section);
                    foreach (var command in commandList)
                    {
                        _allCommands[command.Command] = command;
                    }
                }
                else
                {
                    throw new InvalidOperationException($"Unknown section type in file path: {filePath}");
                }
            }
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException("Failed to initialize schema service", ex);
        }
    }

    public CommandDefinition? GetCommand(string name)
    {
        _allCommands.TryGetValue(name, out var command);
        return command;
    }

    private static string ExtractSectionName(string filePath)
    {
        // Extract section name from path like "data/commandschema/player/mouse.json"
        var parts = filePath.Split('/');

        var fileName = Path.GetFileNameWithoutExtension(parts[^1]);
        return fileName;
    }

    private static string FormatDisplayName(string sectionName)
    {
        return char.ToUpper(sectionName[0]) + sectionName[1..];
    }
}
