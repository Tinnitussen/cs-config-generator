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
        // Note: Don't initialize defaults here since schema might not be loaded yet
    }

    /// <summary>
    /// Initialize settings with default values from the schema
    /// This should be called after the schema is loaded
    /// </summary>
    public void InitializeDefaultValues()
    {
        _settings.Clear();
        
        foreach (var command in _schemaService.Commands)
        {
            var defaultValue = GetDefaultValueForCommand(command);
            _settings[command.Name] = defaultValue;
        }
        
        NotifyStateChanged();
    }

    /// <summary>
    /// Gets the appropriate default value for a command
    /// </summary>
    private object GetDefaultValueForCommand(CommandDefinition command)
    {
        if (command.DefaultValue != null)
        {
            return ConvertJsonValueToCorrectType(command.DefaultValue, command.Type);
        }
        
        // Fallback defaults
        return command.Type switch
        {
            CommandValueType.Boolean => false,
            CommandValueType.Numeric => 0f,
            CommandValueType.Enum => command.Options?.Keys.FirstOrDefault() ?? "0",
            _ => string.Empty
        };
    }

    /// <summary>
    /// Updates a single setting and notifies subscribers
    /// </summary>
    public void UpdateSetting(string commandName, object value)
    {
        var command = _schemaService.Commands.FirstOrDefault(c => c.Name == commandName);
        if (command != null)
        {
            var convertedValue = ConvertJsonValueToCorrectType(value, command.Type);
            _settings[commandName] = convertedValue;
            NotifyStateChanged();
        }
    }

    /// <summary>
    /// Gets the current value for a command, or the default if not set
    /// </summary>
    public object GetSetting(string commandName)
    {
        if (_settings.TryGetValue(commandName, out var value))
            return value;
            
        var command = _schemaService.Commands.FirstOrDefault(c => c.Name == commandName);
        return command != null ? GetDefaultValueForCommand(command) : string.Empty;
    }

    /// <summary>
    /// Converts a value to the correct type, handling JsonElement properly
    /// </summary>
    private static object ConvertJsonValueToCorrectType(object value, CommandValueType type)
    {
        // Handle JsonElement from JSON deserialization
        if (value is JsonElement element)
        {
            switch (type)
            {
                case CommandValueType.Boolean:
                    return element.ValueKind switch
                    {
                        JsonValueKind.True => true,
                        JsonValueKind.False => false,
                        JsonValueKind.String => ParseBooleanFromString(element.GetString() ?? "false"),
                        JsonValueKind.Number => element.GetInt32() != 0,
                        _ => false
                    };

                case CommandValueType.Numeric:
                    return element.ValueKind switch
                    {
                        JsonValueKind.Number => element.GetSingle(),
                        JsonValueKind.String => ParseFloatFromString(element.GetString() ?? "0"),
                        _ => 0f
                    };

                case CommandValueType.Enum:
                case CommandValueType.String:
                default:
                    return element.ValueKind switch
                    {
                        JsonValueKind.String => element.GetString() ?? string.Empty,
                        JsonValueKind.Number => element.GetRawText(),
                        JsonValueKind.True => "true",
                        JsonValueKind.False => "false",
                        _ => element.ToString()
                    };
            }
        }

        // Handle regular .NET types
        return type switch
        {
            CommandValueType.Boolean => ConvertToBoolean(value),
            CommandValueType.Numeric => ConvertToFloat(value),
            CommandValueType.Enum => value.ToString() ?? "0",
            _ => value.ToString() ?? string.Empty
        };
    }

    private static bool ConvertToBoolean(object value)
    {
        if (value is bool b) return b;
        if (value is string str) return ParseBooleanFromString(str);
        if (value is int i) return i != 0;
        if (value is float f) return f != 0;
        return Convert.ToBoolean(value);
    }

    private static bool ParseBooleanFromString(string str)
    {
        return str switch
        {
            "0" => false,
            "1" => true,
            "true" => true,
            "false" => false,
            _ => bool.Parse(str)
        };
    }

    private static float ConvertToFloat(object value)
    {
        if (value is float f) return f;
        if (value is string str) return ParseFloatFromString(str);
        return Convert.ToSingle(value);
    }

    private static float ParseFloatFromString(string str)
    {
        if (float.TryParse(str, NumberStyles.Any, CultureInfo.InvariantCulture, out var result))
            return result;
        return 0f;
    }

    /// <summary>
    /// Generates a config file based on current settings
    /// </summary>
    public string GenerateConfigFile()
    {
        var builder = new StringBuilder();
        builder.AppendLine("// Generated by CS Config Generator");
        builder.AppendLine($"// Generated on: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
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

            // Split on first space to handle values with spaces
            var firstSpaceIndex = trimmedLine.IndexOf(' ');
            if (firstSpaceIndex <= 0) continue;

            var commandName = trimmedLine[..firstSpaceIndex].Trim();
            var valueStr = trimmedLine[(firstSpaceIndex + 1)..].Trim().Trim('"');

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
            CommandValueType.Boolean => ParseBooleanFromString(valueStr),
            CommandValueType.Numeric => ParseFloatFromString(valueStr),
            _ => valueStr
        };
    }

    /// <summary>
    /// Resets all settings to their default values
    /// </summary>
    public void ResetToDefaults()
    {
        InitializeDefaultValues();
    }

    private void NotifyStateChanged() => OnStateChange?.Invoke();
}