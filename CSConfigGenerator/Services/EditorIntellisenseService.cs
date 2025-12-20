using CSConfigGenerator.Interfaces;
using CSConfigGenerator.Models;
using Microsoft.JSInterop;

namespace CSConfigGenerator.Services;

/// <summary>
/// Initializes Monaco editor with CS2 command intellisense support.
/// </summary>
public class EditorIntellisenseService : IEditorIntellisenseService
{
    private readonly ISchemaService _schemaService;
    private readonly IJSRuntime _jsRuntime;
    private bool _isInitialized;
    private readonly SemaphoreSlim _initLock = new(1, 1);

    public bool IsInitialized => _isInitialized;

    public EditorIntellisenseService(ISchemaService schemaService, IJSRuntime jsRuntime)
    {
        _schemaService = schemaService;
        _jsRuntime = jsRuntime;
    }

    public async Task InitializeAsync()
    {
        if (_isInitialized)
            return;

        await _initLock.WaitAsync();
        try
        {
            // Double-check after acquiring lock
            if (_isInitialized)
                return;

            // Transform commands to completion data
            var completionData = _schemaService.Commands
                .Select(CommandCompletionData.FromCommandDefinition)
                .ToArray();

            // Call JavaScript to initialize the language
            await _jsRuntime.InvokeVoidAsync("initCs2ConfigLanguage", (object)completionData);

            _isInitialized = true;
        }
        finally
        {
            _initLock.Release();
        }
    }
}
