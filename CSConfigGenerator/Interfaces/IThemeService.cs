using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface IThemeService
{
    Task InitializeAsync();
    Task SetThemeAsync(Theme theme);
    Theme CurrentTheme { get; }
    string EffectiveThemeClass { get; }
    event Action? OnThemeChanged;
}
