namespace CSConfigGenerator.Models;

/// <summary>
/// Defines the data type of a console variable.
/// This enum is used to determine which UI component to render.
/// </summary>
public enum CommandValueType
{
    Boolean,
    Numeric,
    String,
    Enum
}