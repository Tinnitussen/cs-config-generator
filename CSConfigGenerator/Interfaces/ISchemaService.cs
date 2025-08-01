using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface ISchemaService
{
    IReadOnlyList<ConfigSection> Sections { get; }
    IReadOnlyList<ConfigSection> PlayerSections { get; }
    IReadOnlyList<ConfigSection> ServerSections { get; }
    Task InitializeAsync();
    CommandDefinition? GetCommand(string name);
    CommandDefinition? GetPlayerCommand(string name);
    CommandDefinition? GetServerCommand(string name);
}