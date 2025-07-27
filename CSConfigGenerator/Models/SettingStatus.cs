namespace CSConfigGenerator.Models;

public enum SettingStatus
{
    /// <summary>
    /// Default state for commands that should be visible in the UI and included in the config file.
    /// </summary>
    Visible,

    /// <summary>
    /// Default state for commands that are hidden from the UI and config file by default.
    /// </summary>
    Hidden,

    /// <summary>
    /// State for a 'Visible' command that has been removed by the user.
    /// It is now hidden from the config file but may be shown in the UI as 'restorable'.
    /// </summary>
    Removed,

    /// <summary>
    /// State for a 'Hidden' command that has been explicitly added by the user.
    /// It is now visible in the UI and included in the config file.
    /// </summary>
    Added
}