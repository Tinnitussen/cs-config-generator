using CSConfigGenerator.Models;

namespace CSConfigGenerator.Services;

public interface ISchemaService
{
    IReadOnlyList<ConfigSection> Sections { get; }
    Task InitializeAsync();
    CommandDefinition? GetCommand(string name);
}