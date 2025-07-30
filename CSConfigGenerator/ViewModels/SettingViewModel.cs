using CSConfigGenerator.Models;
using CSConfigGenerator.Services;

namespace CSConfigGenerator.ViewModels;

public class SettingViewModel(CommandDefinition command, IConfigStateService configState)
{
    private readonly IConfigStateService _configState = configState;
    public CommandDefinition Command { get; } = command;
    public Setting Setting => _configState.GetSetting(Command.Command);

    public object Value
    {
        get => Setting.Value;
        set => _configState.SetValue(Command.Command, value);
    }

    public string StatusBadgeClass => Setting.IsInConfigEditor ? "bg-success" : "bg-secondary";

    public void Add() => _configState.SetIncluded(Command.Command, true);
    public void Remove() => _configState.SetIncluded(Command.Command, false);
    public void Restore() => _configState.SetIncluded(Command.Command, true);
}