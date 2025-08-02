using CSConfigGenerator.Models;
using CSConfigGenerator.Interfaces;

namespace CSConfigGenerator.Services;

public class PlayerConfigStateService : ConfigStateServiceBase
{
    public PlayerConfigStateService(ISchemaService schemaService)
        : base(schemaService, schemaService.PlayerSections, schemaService.GetPlayerCommand)
    {
    }

    protected override string GetConfigFileHeader()
    {
        return "// Player Configuration";
    }
}
