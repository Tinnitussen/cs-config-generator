namespace CSConfigGenerator.Models;

public record ConfigSection
{
    public required string Name { get; init; }
    public required string DisplayName { get; init; }
    public required IReadOnlyList<CommandDefinition> Commands { get; init; }
}
