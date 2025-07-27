using CSConfigGenerator.Models;
using CSConfigGenerator.Services;

namespace CSConfigGenerator.ViewModels;

public class SettingViewModel(CommandDefinition command, IConfigStateService configState)
{
    private readonly IConfigStateService _configState = configState;
    public CommandDefinition Command { get; } = command;

    // The ViewModel gets the Setting, but doesn't store it long-term.
    // It always asks the service for the current truth.
    public Setting Setting => _configState.GetSetting(Command.Name);

    // Value property for two-way binding now requests changes from the service.
    public object Value
    {
        get => Setting.Value;
        set
        {
            if (Setting.Value.Equals(value)) return;
            _configState.UpdateSetting(Command.Name, s => s.Value = value);
        }
    }

    public string StatusBadgeClass => Setting.Status switch
    {
        SettingStatus.Visible => "bg-info text-dark",
        SettingStatus.Added => "bg-success",
        SettingStatus.Removed => "bg-warning text-dark",
        SettingStatus.Hidden => "bg-secondary",
        _ => "bg-light text-dark"
    };
    
    public void Add()
    {
        _configState.UpdateSetting(Command.Name, s => 
            s.Status = s.Status == SettingStatus.Hidden ? SettingStatus.Added : SettingStatus.Visible
        );
    }
    
    public void Remove()
    {
        _configState.UpdateSetting(Command.Name, s => 
            s.Status = s.Status == SettingStatus.Added ? SettingStatus.Hidden : SettingStatus.Removed
        );
    }
    
    public void Restore()
    {
        _configState.UpdateSetting(Command.Name, s => s.Status = SettingStatus.Visible);
    }
}