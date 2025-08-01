using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface ISchemaService
{
    IReadOnlyList<ConfigSection> Sections { get; }
    Task InitializeAsync();
    CommandDefinition? GetCommand(string name);
}