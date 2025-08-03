using System.Text.Json;
using CSConfigGenerator.Models;
using CSConfigGenerator.Services;
using CSConfigGenerator.Interfaces;
using Xunit;

namespace CSConfigGenerator.Tests;

/// <summary>
/// Custom SchemaService for testing with direct file access
/// </summary>
public class TestSchemaService(string wwwrootPath) : ISchemaService
{
    private readonly string _wwwrootPath = wwwrootPath;
    private readonly List<ConfigSection> _playerSections = [];
    private readonly List<ConfigSection> _serverSections = [];
    private readonly List<ConfigSection> _allSections = [];
    private readonly List<CommandDefinition> _allCommands = [];

    public IReadOnlyList<ConfigSection> PlayerSections => _playerSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> ServerSections => _serverSections.AsReadOnly();
    public IReadOnlyList<ConfigSection> AllSections => _allSections.AsReadOnly();
    public IReadOnlyList<CommandDefinition> AllCommands => _allCommands.AsReadOnly();

    public async Task InitializeAsync()
    {
        var manifestPath = Path.Combine(_wwwrootPath, "data/manifest.json");
        var manifestJson = await File.ReadAllTextAsync(manifestPath);
        var manifest = JsonSerializer.Deserialize<List<string>>(manifestJson, JsonContext.Default.Options)
            ?? throw new InvalidOperationException("Manifest file could not be loaded or is empty.");

        foreach (var filePath in manifest)
        {
            var fullPath = Path.Combine(_wwwrootPath, filePath);
            var commandsJson = await File.ReadAllTextAsync(fullPath);
            var commands = JsonSerializer.Deserialize<List<CommandDefinition>>(commandsJson, JsonContext.Default.ListCommandDefinition);

            if (commands == null) continue;

            var sectionName = Path.GetFileNameWithoutExtension(filePath);
            var section = new ConfigSection
            {
                Name = sectionName,
                DisplayName = sectionName,
                Commands = commands
            };

            // Process the commands similar to SchemaService
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
                _allCommands.AddRange(commands);
            }
        }
    }

    public CommandDefinition? GetPlayerCommand(string name)
    {
        return PlayerSections
            .SelectMany(section => section.Commands)
            .FirstOrDefault(cmd => cmd.Command.Equals(name, StringComparison.OrdinalIgnoreCase));
    }

    public CommandDefinition? GetServerCommand(string name)
    {
        return ServerSections
            .SelectMany(section => section.Commands)
            .FirstOrDefault(cmd => cmd.Command.Equals(name, StringComparison.OrdinalIgnoreCase));
    }

    public CommandDefinition? GetAllCommand(string name)
    {
        return AllCommands
            .FirstOrDefault(cmd => cmd.Command.Equals(name, StringComparison.OrdinalIgnoreCase));
    }
}

public class ManifestValidationTests : IDisposable
{
    private readonly string _wwwrootPath;
    private readonly TestSchemaService _schemaService;

    public ManifestValidationTests()
    {
        // Get path to wwwroot directory for testing
        _wwwrootPath = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(),
            "..", "..", "..", "..",
            "CSConfigGenerator", "wwwroot"));

        // Create a schema service with direct file access
        _schemaService = new TestSchemaService(_wwwrootPath);
    }

    private string GetFullPath(string relativePath)
    {
        return Path.Combine(_wwwrootPath, relativePath);
    }

    private async Task<List<string>?> ReadManifestAsync()
    {
        var manifestPath = GetFullPath("data/manifest.json");
        var json = await File.ReadAllTextAsync(manifestPath);
        return JsonSerializer.Deserialize<List<string>>(json, JsonContext.Default.Options);
    }

    private async Task<List<CommandDefinition>?> ReadCommandsAsync(string relativePath)
    {
        var fullPath = GetFullPath(relativePath);
        var json = await File.ReadAllTextAsync(fullPath);
        return JsonSerializer.Deserialize<List<CommandDefinition>>(json, JsonContext.Default.Options);
    }

    [Fact]
    public async Task ManifestFile_ShouldExist()
    {
        // Act & Assert
        var manifestPath = GetFullPath("data/manifest.json");
        Assert.True(File.Exists(manifestPath), "Manifest file should exist");

        var manifest = await ReadManifestAsync();
        Assert.NotNull(manifest);
    }

    [Fact]
    public async Task ManifestFile_ShouldContainValidJsonArray()
    {
        // Act
        var manifestPath = GetFullPath("data/manifest.json");
        var content = await File.ReadAllTextAsync(manifestPath);

        // Assert
        Assert.False(string.IsNullOrWhiteSpace(content), "Manifest file should not be empty");

        var exception = await Record.ExceptionAsync(async () =>
            await Task.FromResult(JsonSerializer.Deserialize<List<string>>(content)));
        Assert.Null(exception);
    }

    [Fact]
    public async Task ManifestFile_ShouldNotBeEmpty()
    {
        // Act
        var manifest = await ReadManifestAsync();

        // Assert
        Assert.NotNull(manifest);
        Assert.NotEmpty(manifest);
    }

    [Fact]
    public async Task ManifestPaths_ShouldFollowExpectedStructure()
    {
        // Act
        var manifest = await ReadManifestAsync();

        // Assert
        Assert.NotNull(manifest);

        foreach (var filePath in manifest)
        {
            Assert.False(string.IsNullOrWhiteSpace(filePath), "File path should not be null or empty");
            Assert.StartsWith("data/commandschema/", filePath);
            Assert.EndsWith(".json", filePath);

            // Should contain one of the expected folder types
            Assert.True(
                filePath.Contains("/player/") ||
                filePath.Contains("/server/") ||
                filePath.Contains("/all/"),
                $"File path '{filePath}' should contain /player/, /server/, or /all/ folder");
        }
    }

    [Fact]
    public async Task AllManifestFiles_ShouldExist()
    {
        // Arrange
        var manifest = await ReadManifestAsync();
        Assert.NotNull(manifest);

        // Act & Assert
        foreach (var filePath in manifest)
        {
            var fullPath = GetFullPath(filePath);
            Assert.True(File.Exists(fullPath),
                $"File '{filePath}' referenced in manifest should exist and be accessible");
        }
    }

    [Fact]
    public async Task AllManifestFiles_ShouldContainValidCommandDefinitions()
    {
        // Arrange
        var manifest = await ReadManifestAsync();
        Assert.NotNull(manifest);

        // Act & Assert
        foreach (var filePath in manifest)
        {
            var commands = await ReadCommandsAsync(filePath);

            Assert.NotNull(commands);
            // It's okay for command files to be empty, but they should deserialize properly

            // If commands exist, validate their structure
            foreach (var command in commands)
            {
                Assert.False(string.IsNullOrWhiteSpace(command.Command),
                    $"Command in '{filePath}' should have a non-empty Command property");
            }
        }
    }

    [Fact]
    public async Task SchemaService_ShouldInitializeWithoutException()
    {
        // Act & Assert
        var exception = await Record.ExceptionAsync(async () =>
        {
            await _schemaService.InitializeAsync();
        });

        Assert.Null(exception);
    }

    [Fact]
    public async Task SchemaService_ShouldLoadSectionsFromManifest()
    {
        // Act
        await _schemaService.InitializeAsync();

        // Assert
        // Should have at least some sections loaded
        Assert.True(_schemaService.PlayerSections.Count > 0 || _schemaService.ServerSections.Count > 0,
            "SchemaService should load at least one section from manifest");
    }

    [Fact]
    public async Task ManifestFiles_ShouldHaveValidJsonStructure()
    {
        // Arrange
        var manifest = await ReadManifestAsync();
        Assert.NotNull(manifest);

        // Act & Assert
        foreach (var filePath in manifest)
        {
            var fullPath = GetFullPath(filePath);
            var content = await File.ReadAllTextAsync(fullPath);

            Assert.False(string.IsNullOrWhiteSpace(content),
                $"File '{filePath}' should not be empty");

            // Test that it's valid JSON
            var jsonException = await Record.ExceptionAsync(() =>
                Task.FromResult(JsonDocument.Parse(content)));
            Assert.True(jsonException == null,
                $"File '{filePath}' should contain valid JSON");

            // Test that it deserializes to the expected type
            var deserializeException = await Record.ExceptionAsync(() =>
                Task.FromResult(JsonSerializer.Deserialize<List<CommandDefinition>>(content, JsonContext.Default.Options)));
            Assert.True(deserializeException == null,
                $"File '{filePath}' should deserialize to List<CommandDefinition>");
        }
    }

    [Theory]
    [InlineData("player")]
    [InlineData("server")]
    public async Task ManifestPaths_ShouldContainExpectedSectionTypes(string sectionType)
    {
        // Arrange
        var manifest = await ReadManifestAsync();
        Assert.NotNull(manifest);

        // Act
        var hasExpectedSection = manifest.Any(path => path.Contains($"/{sectionType}/"));

        // Assert
        Assert.True(hasExpectedSection,
            $"Manifest should contain at least one file with '/{sectionType}/' in the path");
    }

    public void Dispose()
    {
        // No resources to dispose
        GC.SuppressFinalize(this);
    }
}
