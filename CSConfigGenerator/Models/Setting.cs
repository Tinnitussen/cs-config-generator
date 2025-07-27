namespace CSConfigGenerator.Models;

public record Setting
{
    public required object Value { get; set; }
    public bool IsInConfigEditor { get; set; }
}