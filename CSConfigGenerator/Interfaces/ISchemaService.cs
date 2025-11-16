using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface ISchemaService
{
    // Flat list of all commands after initialization
    IReadOnlyList<CommandDefinition> Commands { get; }
    // Initialize service (load manifest & command definitions)
    Task InitializeAsync();
    // Lookup a command definition by its command string
    CommandDefinition? GetCommand(string name);
}
