using CSConfigGenerator.Models;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class PlayerConfigStateService : ConfigStateServiceBase
{
    public PlayerConfigStateService(ISchemaService schemaService) : base(schemaService)
    {
    }

    public override void InitializeDefaults()
    {
        _settings.Clear();

        foreach (var section in _schemaService.PlayerSections)
        {
            foreach (var command in section.Commands)
            {
                var defaultValue = SettingTypeHelpers.ConvertFromJson(command.UiData.Type, command.UiData.DefaultValue);
                _settings[command.Command] = new Setting
                {
                    Value = defaultValue,
                    IsInConfigEditor = !command.UiData.HideFromDefaultView
                };
            }
        }

        NotifyStateChanged();
    }

    protected override string GetConfigFileHeader()
    {
        return "// Player Configuration";
    }

    protected override IReadOnlyList<ConfigSection> GetSections()
    {
        return _schemaService.PlayerSections;
    }

    protected override CommandDefinition? GetCommandDefinition(string commandName)
    {
        return _schemaService.GetPlayerCommand(commandName);
    }
}