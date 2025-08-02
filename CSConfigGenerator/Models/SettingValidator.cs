using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Reflection;
using System.Text.RegularExpressions;

namespace CSConfigGenerator.Models;

/// <summary>
/// Provides validation functionality for settings based on their type
/// </summary>
public static class SettingValidator
{
    /// <summary>
    /// Validates that a value string can be parsed according to the setting type
    /// </summary>
    /// <param name="settingType">The type of setting to validate against</param>
    /// <param name="valueStr">The string value to validate</param>
    /// <returns>A tuple containing whether the validation was successful and any error message</returns>
    public static (bool IsValid, string? ErrorMessage) Validate(SettingType settingType, string valueStr)
    {
        // Get the RegularExpression attribute if one exists
        var regexAttr = GetEnumAttribute<RegularExpressionAttribute>(settingType);
        if (regexAttr != null)
        {
            if (!Regex.IsMatch(valueStr, regexAttr.Pattern))
            {
                return (false, regexAttr.ErrorMessage);
            }
        }

        // For numeric types, try to parse and check range
        var rangeAttr = GetEnumAttribute<RangeAttribute>(settingType);
        if (rangeAttr != null)
        {
            if (settingType is SettingType.Int or SettingType.Bitmask or SettingType.UnknownInteger)
            {
                if (!int.TryParse(valueStr, NumberStyles.Integer, CultureInfo.InvariantCulture, out int intValue))
                {
                    return (false, $"Value must be a valid integer");
                }

                if (intValue < (int) rangeAttr.Minimum || intValue > (int) rangeAttr.Maximum)
                {
                    return (false, rangeAttr.ErrorMessage);
                }
            }
            else if (settingType is SettingType.Float or SettingType.UnknownNumeric)
            {
                if (!float.TryParse(valueStr, NumberStyles.Float, CultureInfo.InvariantCulture, out float floatValue))
                {
                    return (false, $"Value must be a valid floating point number");
                }

                if ((double) floatValue < (double) rangeAttr.Minimum || (double) floatValue > (double) rangeAttr.Maximum)
                {
                    return (false, rangeAttr.ErrorMessage);
                }
            }
        }

        // Boolean values need special handling
        if (settingType == SettingType.Bool)
        {
            if (valueStr is not "true" and not "false" and not "1" and not "0")
            {
                return (false, "Boolean value must be 'true', 'false', '1', or '0'");
            }
        }

        return (true, null);
    }

    /// <summary>
    /// Gets a specific attribute from an enum value if it exists
    /// </summary>
    private static T? GetEnumAttribute<T>(SettingType value) where T : Attribute
    {
        var type = typeof(SettingType);
        var memberInfo = type.GetMember(value.ToString());
        if (memberInfo.Length > 0)
        {
            return memberInfo[0].GetCustomAttribute<T>();
        }
        return null;
    }
}
