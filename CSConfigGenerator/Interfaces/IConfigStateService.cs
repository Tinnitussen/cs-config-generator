using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface IConfigStateService
{
    IReadOnlyDictionary<string, Setting> Settings { get; }
    event Action<object?>? OnStateChange;

    void InitializeDefaults();
    Setting GetSetting(string commandName);
    void SetValue(string commandName, object value, object? originator = null);
    void SetIncluded(string commandName, bool IsInConfigEditor, object? originator = null);

    string GenerateConfigFile();
    void ParseConfigFile(string configText, object? originator = null);
    void ResetToDefaults();
}
