using System.Net.Http.Json;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class PresetService : IPresetService
{
    private readonly HttpClient _http;

    public PresetService(HttpClient http)
    {
        _http = http;
    }

    public async Task<List<string>> GetPresetNamesAsync(string presetType)
    {
        var manifestUrl = $"data/presets/{presetType}/manifest.json";
        try
        {
            var presets = await _http.GetFromJsonAsync<List<string>>(manifestUrl);
            return presets ?? new List<string>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Could not fetch or parse preset manifest for {presetType}: {ex.Message}");
            return new List<string>();
        }
    }

    public async Task<string> GetPresetContentAsync(string presetType, string presetName)
    {
        var presetUrl = $"data/presets/{presetType}/{presetName}.cfg";
        try
        {
            return await _http.GetStringAsync(presetUrl);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Could not fetch preset content for {presetType}/{presetName}: {ex.Message}");
            return string.Empty;
        }
    }
}
