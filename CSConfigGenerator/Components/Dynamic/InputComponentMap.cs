using CSConfigGenerator.Models;
using Microsoft.AspNetCore.Components.Forms;

namespace CSConfigGenerator.Components.Dynamic;

/// <summary>
/// A static class that maps a CommandValueType to a specific Blazor component type.
/// This is used by the DynamicInput component to determine which input to render.
/// </summary>
public static class InputComponentMap
{
    private static readonly Dictionary<CommandValueType, Type> _map = new()
    {
        { CommandValueType.Boolean, typeof(InputCheckbox) },
        { CommandValueType.Numeric, typeof(InputNumber<>) }, // Note: This is a generic type
        { CommandValueType.String, typeof(InputText) },
        { CommandValueType.Enum, typeof(InputSelect<>) }    // Note: This is a generic type
    };

    /// <summary>
    /// Gets the corresponding component type for a given command value type.
    /// </summary>
    /// <param name="type">The command's value type.</param>
    /// <returns>The Blazor component type to render.</returns>
    public static Type GetComponentTypeFor(CommandValueType type)
    {
        return _map.TryGetValue(type, out var componentType) ? componentType : typeof(InputText); // Default to InputText
    }
}
