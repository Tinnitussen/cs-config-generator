using System.Globalization;
using System.Text;
using System.Text.Json;
using CSConfigGenerator.Models;

namespace CSConfigGenerator.Services;

public class ConfigStateService
{
    private readonly Dictionary<string, object> _settings = new();
    private readonly SchemaService _schemaService;
    
    public event Action? OnStateChange;

    /// <summary>
    /// Gets a read-only view of all current settings
    /// </summary>
    public IReadOnlyDictionary<string, object> Settings => _settings.AsReadOnly();

    public ConfigStateService(SchemaService schemaService)
    {
        _schemaService = schemaService;
        InitializeDefaultValues();
    }

    /// <summary>
    /// Initialize settings with default values from the schema
    /// </summary>
    private void InitializeDefaultValues()
    {
        foreach (var command in _schemaService.Commands)
        {
            if (command.DefaultValue != null)
            {
                var convertedValue = ConvertValueToCorrectType(command.DefaultValue, command.Type);
                _settings[command.Name] = convertedValue;
            }
            else
            {
                // Provide sensible defaults if no default is specified
                _settings[command.Name] = command.Type switch
                {
                    CommandValueType.Boolean => false,
                    CommandValueType.Numeric => 0f,
                    CommandValueType.Enum => command.Options?.Keys.FirstOrDefault() ?? "0",
                    _ => string.Empty
                };
            }
        }
    }

    /// <summary>
    /// Updates a single setting and notifies subscribers
    /// </summary>
    public void UpdateSetting(string commandName, object value)
    {
        var command = _schemaService.Commands.FirstOrDefault(c => c.Name == commandName);
        if (command != null)
        {
            var convertedValue = ConvertValueToCorrectType(value, command.Type);
            _settings[commandName] = convertedValue;
            NotifyStateChanged();
        }
    }

    /// <summary>
    /// Gets the current value for a command, or the default if not set
    /// </summary>
    public object GetSetting(string commandName)
    {
        return _settings.TryGetValue(commandName, out var value) ? value : GetDefaultForCommand(commandName);
    }

    /// <summary>
    /// Converts a value to the correct type based on the command definition
    /// </summary>
    private static object ConvertValueToCorrectType(object value, CommandValueType type)
    {
         if (value is JsonElement element)
    {
        switch (type)
        {
            case CommandValueType.Boolean:
                if (element.ValueKind == JsonValueKind.True || element.ValueKind == JsonValueKind.False)
                    return element.GetBoolean();
                else if (element.ValueKind == JsonValueKind.String)
                {
                    var s = element.GetString();
                    if (s == "0") return false;
                    if (s == "1") return true;
                    return bool.Parse(s);
                }
                break;
            case CommandValueType.Numeric:
                if (element.ValueKind == JsonValueKind.Number)
                    return element.GetSingle();
                else if (element.ValueKind == JsonValueKind.String)
                {
                    if (float.TryParse(element.GetString(), NumberStyles.Any, CultureInfo.InvariantCulture, out var parsed))
                    {
                        return parsed;
                    }
                    throw new InvalidCastException($"Unable to parse '{element.GetString()}' as a float.");
                }
                break;
            case CommandValueType.Enum:
                return element.ValueKind == JsonValueKind.String ? element.GetString() ?? "0" : element.ToString();
            default:
                return element.ToString() ?? string.Empty;
        }
    }

    // For non-JsonElement values, add extra handling for booleans
    return type switch
    {
        CommandValueType.Boolean => value is string str 
                                        ? (str == "0" ? false : str == "1" ? true : bool.Parse(str))
                                        : Convert.ToBoolean(value),
        CommandValueType.Numeric => Convert.ToSingle(value),
        CommandValueType.Enum => value.ToString() ?? "0",
        _ => value.ToString() ?? string.Empty
    };
    }

    /// <summary>
    /// Gets the default value for a command
    /// </summary>
    private object GetDefaultForCommand(string commandName)
    {
        var command = _schemaService.Commands.FirstOrDefault(c => c.Name == commandName);
        return command?.Type switch
        {
            CommandValueType.Boolean => false,
            CommandValueType.Numeric => 0f,
            CommandValueType.Enum => command.Options?.Keys.FirstOrDefault() ?? "0",
            _ => string.Empty
        };
    }

    /// <summary>
    /// Generates a config file based on current settings
    /// </summary>
    public string GenerateConfigFile()
    {
        var builder = new StringBuilder();
        builder.AppendLine("// Generated by CS Config Generator");
        builder.AppendLine();

        foreach (var command in _schemaService.Commands)
        {
            if (_settings.TryGetValue(command.Name, out var value))
            {
                var formattedValue = FormatValueForConfig(value, command.Type);
                builder.AppendLine($"{command.Name} \"{formattedValue}\"");
            }
        }

        return builder.ToString();
    }

    /// <summary>
    /// Formats a value appropriately for the config file
    /// </summary>
    private static string FormatValueForConfig(object value, CommandValueType type)
    {
        return type switch
        {
            CommandValueType.Boolean => ((bool)value) ? "1" : "0",
            CommandValueType.Numeric => ((float)value).ToString(CultureInfo.InvariantCulture),
            _ => value.ToString() ?? string.Empty
        };
    }

    /// <summary>
    /// Parses a config file and updates the current state
    /// </summary>
    public void ParseAndUpdateState(string rawConfig)
    {
        var lines = rawConfig.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries);
        
        foreach (var line in lines)
        {
            // Skip comments and empty lines
            var trimmedLine = line.Trim();
            if (string.IsNullOrEmpty(trimmedLine) || trimmedLine.StartsWith("//")) 
                continue;

            var parts = trimmedLine.Split([' '], 2, StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length < 2) continue;

            var commandName = parts[0].Trim();
            var valueStr = parts[1].Trim().Replace("\"", "");

            // Find the command definition to get the correct type
            var command = _schemaService.Commands.FirstOrDefault(c => c.Name == commandName);
            if (command == null) continue;

            try
            {
                var parsedValue = ParseValueFromString(valueStr, command.Type);
                _settings[commandName] = parsedValue;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing value '{valueStr}' for command '{commandName}': {ex.Message}");
            }
        }
        
        NotifyStateChanged();
    }

    /// <summary>
    /// Parses a string value to the appropriate type
    /// </summary>
    private static object ParseValueFromString(string valueStr, CommandValueType type)
    {
        return type switch
        {
            CommandValueType.Boolean => valueStr == "1" || bool.Parse(valueStr),
            CommandValueType.Numeric => float.Parse(valueStr, CultureInfo.InvariantCulture),
            _ => valueStr
        };
    }

    /// <summary>
    /// Resets all settings to their default values
    /// </summary>
    public void ResetToDefaults()
    {
        _settings.Clear();
        InitializeDefaultValues();
        NotifyStateChanged();
    }

    private void NotifyStateChanged() => OnStateChange?.Invoke();
}