using CSConfigGenerator.Models;
using Xunit;

namespace CSConfigGenerator.Tests;

public class SettingValidatorTests
{
    [Theory]
    [InlineData(SettingType.Bool, "true", true)]
    [InlineData(SettingType.Bool, "false", true)]
    [InlineData(SettingType.Bool, "1", true)]
    [InlineData(SettingType.Bool, "0", true)]
    [InlineData(SettingType.Bool, "yes", false)] // Invalid
    [InlineData(SettingType.Bool, "no", false)] // Invalid
    [InlineData(SettingType.Int, "42", true)]
    [InlineData(SettingType.Int, "-42", true)]
    [InlineData(SettingType.Int, "3.14", false)] // Invalid
    [InlineData(SettingType.Float, "42", true)]
    [InlineData(SettingType.Float, "42.5", true)]
    [InlineData(SettingType.Float, "-42.5", true)]
    [InlineData(SettingType.Float, "abc", false)] // Invalid
    [InlineData(SettingType.String, "any value", true)] // Always valid
    [InlineData(SettingType.Enum, "ANY_VALUE", true)] // Always valid
    [InlineData(SettingType.Bitmask, "42", true)]
    [InlineData(SettingType.Bitmask, "abc", false)] // Invalid
    public void Validate_ChecksValueAgainstSettingType(SettingType settingType, string value, bool expectedIsValid)
    {
        // Act
        var (isValid, _) = SettingValidator.Validate(settingType, value);
        
        // Assert
        Assert.Equal(expectedIsValid, isValid);
    }
}
