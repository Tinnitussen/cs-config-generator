using CSConfigGenerator.Models;

namespace CSConfigGenerator.Services;

public interface IConfigStateService
{
    IReadOnlyDictionary<string, Setting> Settings { get; }
    event Action<object?>? OnStateChange;

    void InitializeDefaults();
    Setting GetSetting(string commandName);
    void SetValue(string commandName, object value, object? originator = null);
    void AddSetting(string commandName, object? originator = null);
    void RemoveSetting(string commandName, object? originator = null);
    void RestoreSetting(string commandName, object? originator = null);
    
    string GenerateConfigFile();
    void ParseConfigFile(string configText, object? originator = null);
    void ResetToDefaults();
}