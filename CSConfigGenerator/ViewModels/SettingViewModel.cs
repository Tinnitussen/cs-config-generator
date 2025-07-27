using CSConfigGenerator.Models;
using CSConfigGenerator.Services;

namespace CSConfigGenerator.ViewModels;

public class SettingViewModel(CommandDefinition command, IConfigStateService configState)
{
    private readonly IConfigStateService _configState = configState;
    public CommandDefinition Command { get; } = command;
    public Setting Setting => _configState.GetSetting(Command.Name);

    public object Value
    {
        get => Setting.Value;
        set => _configState.SetValue(Command.Name, value);
    }

    public string StatusBadgeClass => Setting.Status switch
    {
        SettingStatus.Visible => "bg-info text-dark",
        SettingStatus.Added => "bg-success",
        SettingStatus.Removed => "bg-warning text-dark",
        SettingStatus.Hidden => "bg-secondary",
        _ => "bg-light text-dark"
    };
    
    public void Add() => _configState.AddSetting(Command.Name);
    public void Remove() => _configState.RemoveSetting(Command.Name);
    public void Restore() => _configState.RestoreSetting(Command.Name);
}