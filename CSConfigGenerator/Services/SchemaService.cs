using System.Net.Http.Json;
using CSConfigGenerator.Models;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class SchemaService(HttpClient httpClient) : ISchemaService
{
    private readonly HttpClient _httpClient = httpClient;
    private readonly List<ConfigSection> _playerSections = [];
    private readonly List<ConfigSection> _serverSections = [];
    private readonly List<ConfigSection> _uncategorizedSections = [];
    private readonly List<CommandDefinition> _allCommands = [];
    private readonly Dictionary<string, CommandDefinition> _playerCommandsByName = [];
    private readonly Dictionary<string, CommandDefinition> _serverCommandsByName = [];

    public IReadOnlyList<ConfigSection> PlayerSections => _playerSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> ServerSections => _serverSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> UncategorizedSections => _uncategorizedSections.AsReadOnly();
    public IReadOnlyList<CommandDefinition> AllCommands => _allCommands.AsReadOnly();

    public async Task InitializeAsync()
    {
        try
        {
            // Load the single, large JSON file for the "All Commands" tab first.
            var allCommandsList = await _httpClient.GetFromJsonAsync<List<CommandDefinition>>("data/commandschema/uncategorized/data.json", JsonContext.Default.ListCommandDefinition);
            if (allCommandsList != null)
            {
                _allCommands.AddRange(allCommandsList);
            }

            // Load the section-based files for the Player and Server UI tabs from the manifest.
            var manifest = await _httpClient.GetFromJsonAsync("data/manifest.json", JsonContext.Default.ListString)
                ?? throw new InvalidOperationException("Manifest file could not be loaded or is empty.");

            foreach (var filePath in manifest)
            {
                var commands = await _httpClient.GetFromJsonAsync(filePath, JsonContext.Default.ListCommandDefinition);
                if (commands == null) continue;

                var commandList = commands.AsReadOnly();
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
                // Obsolete 'shared' and 'uncategorized' sections are no longer processed here.
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

    private static string ExtractSectionName(string filePath)
    {
        var fileName = Path.GetFileNameWithoutExtension(filePath);
        return fileName;
    }

    private static string FormatDisplayName(string sectionName)
    {
        return char.ToUpper(sectionName[0]) + sectionName[1..];
    }
}
