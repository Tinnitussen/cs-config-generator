using CSConfigGenerator.Interfaces;
using CSConfigGenerator.Models;
using Microsoft.JSInterop;

namespace CSConfigGenerator.Services;

public class ThemeService : IThemeService
{
    private const string ThemeKey = "theme";
    private readonly ILocalStorageService _localStorageService;
    private readonly IJSRuntime _jsRuntime;
    private Theme _currentTheme;
    private bool _isSystemDark;

    public event Action? OnThemeChanged;

    public ThemeService(ILocalStorageService localStorageService, IJSRuntime jsRuntime)
    {
        _localStorageService = localStorageService;
        _jsRuntime = jsRuntime;
    }

    public Theme CurrentTheme
    {
        get => _currentTheme;
        private set
        {
            if (_currentTheme != value)
            {
                _currentTheme = value;
                OnThemeChanged?.Invoke();
            }
        }
    }

    public string EffectiveThemeClass
    {
        get
        {
            var isDark = CurrentTheme == Theme.Dark || (CurrentTheme == Theme.System && _isSystemDark);
            return isDark ? "dark-theme" : "";
        }
    }

    public async Task InitializeAsync()
    {
        _isSystemDark = await _jsRuntime.InvokeAsync<bool>("isDarkMode");
        var savedTheme = await _localStorageService.GetItemAsync<Theme?>(ThemeKey);
        _currentTheme = savedTheme ?? Theme.System;
        OnThemeChanged?.Invoke();
    }

    public async Task SetThemeAsync(Theme theme)
    {
        CurrentTheme = theme;
        await _localStorageService.SetItemAsync(ThemeKey, theme);
    }
}
