namespace CSConfigGenerator.Interfaces;

/// <summary>
/// Service for initializing Monaco editor intellisense with CS2 command data.
/// </summary>
public interface IEditorIntellisenseService
{
    /// <summary>
    /// Whether the intellisense language has been initialized.
    /// </summary>
    bool IsInitialized { get; }

    /// <summary>
    /// Initialize the CS2 config language in Monaco with command data.
    /// Safe to call multiple times - will only initialize once.
    /// </summary>
    Task InitializeAsync();
}
