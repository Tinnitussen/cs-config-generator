using CSConfigGenerator.Models;

namespace CSConfigGenerator.Services;

public interface IConfigStateService
{
    IReadOnlyDictionary<string, Setting> Settings { get; }
    event Action<object?>? OnStateChange;

    void InitializeDefaults();
    Setting GetSetting(string commandName);
    void UpdateSetting(string commandName, Action<Setting> updateAction, object? originator = null);
    string GenerateConfigFile();
    void ParseConfigFile(string configText, object? originator = null);
    void ResetToDefaults();
}