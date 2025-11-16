using System.Net.Http.Json;
using CSConfigGenerator.Models;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class SchemaService(HttpClient httpClient) : ISchemaService
{
    private readonly List<CommandDefinition> _commands = [];
    private readonly Dictionary<string, CommandDefinition> _commandMap = [];
    public IReadOnlyList<CommandDefinition> Commands => _commands.AsReadOnly();

    public async Task InitializeAsync()
    {
        try
        {
            var manifest = await httpClient.GetFromJsonAsync("data/manifest.json", JsonContext.Default.ListString)
                ?? throw new InvalidOperationException("Manifest file could not be loaded or is empty.");

            foreach (var filePath in manifest)
            {
                var commands = await httpClient.GetFromJsonAsync(filePath, JsonContext.Default.ListCommandDefinition);
                if (commands == null) continue;

                foreach (var command in commands)
                {
                    // Overwrite if duplicate command names appear; latest wins
                    _commandMap[command.Command] = command;
                }
            }

            // Preserve deterministic ordering (alphabetical) for UI consistency
            _commands.AddRange(_commandMap.Values.OrderBy(c => c.Command));
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException("Failed to initialize schema service", ex);
        }
    }

    public CommandDefinition? GetCommand(string name)
    {
        _commandMap.TryGetValue(name, out var command);
        return command;
    }
}
