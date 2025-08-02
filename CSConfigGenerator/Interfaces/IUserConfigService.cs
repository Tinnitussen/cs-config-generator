namespace CSConfigGenerator.Interfaces;

public interface IUserConfigService
{
    Task<List<string>> GetConfigNamesAsync(string configType);
    Task<string> GetConfigContentAsync(string configType, string configName);
    Task SaveConfigAsync(string configType, string configName, string content);
    Task DeleteConfigAsync(string configType, string configName);
}
