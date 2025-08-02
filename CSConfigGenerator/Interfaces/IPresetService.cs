namespace CSConfigGenerator.Interfaces;

public interface IPresetService
{
    Task<List<string>> GetPresetNamesAsync(string presetType);
    Task<string> GetPresetContentAsync(string presetType, string presetName);
}
