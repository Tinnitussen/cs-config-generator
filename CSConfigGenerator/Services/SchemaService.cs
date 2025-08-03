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
    private readonly List<CommandDefinition> _allCommands = [];

    private readonly Dictionary<string, CommandDefinition> _playerCommandsByName = [];
    private readonly Dictionary<string, CommandDefinition> _serverCommandsByName = [];
    private readonly Dictionary<string, CommandDefinition> _allCommandsByName = [];

    public IReadOnlyList<ConfigSection> PlayerSections => _playerSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> ServerSections => _serverSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> AllSections => _allSections.AsReadOnly();
    public IReadOnlyList<CommandDefinition> AllCommands => _allCommands.AsReadOnly();

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
                    foreach (var command in commandList)
                    {
                        _playerCommandsByName[command.Command] = command;
                    }
                }
                else if (filePath.Contains("/server/"))
                {
                    _serverSections.Add(section);
                    foreach (var command in commandList)
                    {
                        _serverCommandsByName[command.Command] = command;
                    }
                }
                else if (filePath.Contains("/all/"))
                {
                    _allSections.Add(section);
                    _allCommands.AddRange(commandList);
                    foreach (var command in commandList)
                    {
                        _allCommandsByName[command.Command] = command;
                    }
                }
                else
                {
                    // For now, we'll just ignore unknown section types.
                    // In the future, we might want to log this.
                }
            }
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException("Failed to initialize schema service", ex);
        }
    }
    public CommandDefinition? GetPlayerCommand(string name)
    {
        _playerCommandsByName.TryGetValue(name, out var command);
        return command;
    }

    public CommandDefinition? GetServerCommand(string name)
    {
        _serverCommandsByName.TryGetValue(name, out var command);
        return command;
    }

    public CommandDefinition? GetAllCommand(string name)
    {
        _allCommandsByName.TryGetValue(name, out var command);
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
