using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface ISchemaService
{
    IReadOnlyList<ConfigSection> PlayerSections { get; }
    IReadOnlyList<ConfigSection> ServerSections { get; }
    Task InitializeAsync();
    CommandDefinition? GetCommand(string name);
}
