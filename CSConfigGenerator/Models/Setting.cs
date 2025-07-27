namespace CSConfigGenerator.Models;

public record Setting
{
    public required object Value { get; set; }
    public required SettingStatus Status { get; set; }
}