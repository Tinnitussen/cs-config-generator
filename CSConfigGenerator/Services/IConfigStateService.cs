namespace CSConfigGenerator.Services;

public interface IConfigStateService
{
    IReadOnlyDictionary<string, object> Settings { get; }
    event Action? OnStateChange;
    
    void InitializeDefaults();
    void UpdateSetting(string commandName, object value);
    T GetSetting<T>(string commandName);
    string GenerateConfigFile();
    void ParseConfigFile(string configText);
    void ResetToDefaults();
}