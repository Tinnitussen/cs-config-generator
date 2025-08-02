using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class UserConfigService : IUserConfigService
{
    private readonly ILocalStorageService _localStorageService;
    private const string StorageKeyPrefix = "user-config-";

    public UserConfigService(ILocalStorageService localStorageService)
    {
        _localStorageService = localStorageService;
    }

    private string GetStorageKey(string configType) => $"{StorageKeyPrefix}{configType}";

    public async Task<List<string>> GetConfigNamesAsync(string configType)
    {
        var configs = await GetConfigsAsync(configType);
        return configs.Keys.ToList();
    }

    public async Task<string> GetConfigContentAsync(string configType, string configName)
    {
        var configs = await GetConfigsAsync(configType);
        return configs.TryGetValue(configName, out var content) ? content : string.Empty;
    }

    public async Task SaveConfigAsync(string configType, string configName, string content)
    {
        var configs = await GetConfigsAsync(configType);
        configs[configName] = content;
        await _localStorageService.SetItemAsync(GetStorageKey(configType), configs);
    }

    public async Task DeleteConfigAsync(string configType, string configName)
    {
        var configs = await GetConfigsAsync(configType);
        if (configs.Remove(configName))
        {
            await _localStorageService.SetItemAsync(GetStorageKey(configType), configs);
        }
    }

    private async Task<Dictionary<string, string>> GetConfigsAsync(string configType)
    {
        var key = GetStorageKey(configType);
        var configs = await _localStorageService.GetItemAsync<Dictionary<string, string>>(key);
        return configs ?? new Dictionary<string, string>();
    }
}
