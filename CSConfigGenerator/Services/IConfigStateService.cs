namespace CSConfigGenerator.Services;

public interface IConfigStateService
{
    IReadOnlyDictionary<string, object> Settings { get; }
    event Action<object?>? OnStateChange;
    
    void InitializeDefaults();
    void UpdateSetting(string commandName, object value, object? originator = null);
    T GetSetting<T>(string commandName);
    string GenerateConfigFile();
    void ParseConfigFile(string configText, object? originator = null);
    void ResetToDefaults();
}