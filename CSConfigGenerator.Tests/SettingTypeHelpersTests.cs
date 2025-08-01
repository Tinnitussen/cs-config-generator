using System.Globalization;
using CSConfigGenerator.Models;
using Xunit;

namespace CSConfigGenerator.Tests;

public class SettingTypeHelpersTests
{
    [Fact]
    public void ParseFromString_Bool_ReturnsCorrectValue()
    {
        // Arrange & Act
        var result1 = SettingTypeHelpers.ParseFromString(SettingType.Bool, "true");
        var result2 = SettingTypeHelpers.ParseFromString(SettingType.Bool, "1");
        var result3 = SettingTypeHelpers.ParseFromString(SettingType.Bool, "false");
        var result4 = SettingTypeHelpers.ParseFromString(SettingType.Bool, "0");
        
        // Assert
        Assert.True((bool)result1);
        Assert.True((bool)result2);
        Assert.False((bool)result3);
        Assert.False((bool)result4);
    }
    
    [Fact]
    public void ParseFromString_Int_ReturnsCorrectValue()
    {
        // Arrange & Act
        var result = SettingTypeHelpers.ParseFromString(SettingType.Int, "42");
        
        // Assert
        Assert.Equal(42, result);
        Assert.IsType<int>(result);
    }
    
    [Fact]
    public void ParseFromString_Float_ReturnsCorrectValue()
    {
        // Arrange & Act
        var result = SettingTypeHelpers.ParseFromString(SettingType.Float, "42.5");
        
        // Assert
        Assert.Equal(42.5f, result);
        Assert.IsType<float>(result);
    }
    
    [Fact]
    public void FormatForConfig_Bool_StandardizesOutput()
    {
        // Arrange & Act
        var result1 = SettingTypeHelpers.FormatForConfig(SettingType.Bool, true);
        var result2 = SettingTypeHelpers.FormatForConfig(SettingType.Bool, "1");
        var result3 = SettingTypeHelpers.FormatForConfig(SettingType.Bool, 1);
        
        // Assert - all formats should be standardized to "true"
        Assert.Equal("true", result1);
        Assert.Equal("true", result2);
        Assert.Equal("true", result3);
    }
    
    [Fact]
    public void FormatForConfig_Int_FormatsCorrectly()
    {
        // Arrange & Act
        var result1 = SettingTypeHelpers.FormatForConfig(SettingType.Int, 42);
        var result2 = SettingTypeHelpers.FormatForConfig(SettingType.Int, "42");
        var result3 = SettingTypeHelpers.FormatForConfig(SettingType.Int, 42.0f);
        
        // Assert
        Assert.Equal("42", result1);
        Assert.Equal("42", result2);
        Assert.Equal("42", result3);
    }
    
    [Fact]
    public void FormatForConfig_Float_FormatsCorrectly()
    {
        // Arrange & Act
        var result1 = SettingTypeHelpers.FormatForConfig(SettingType.Float, 42.5f);
        var result2 = SettingTypeHelpers.FormatForConfig(SettingType.Float, "42.5");
        var result3 = SettingTypeHelpers.FormatForConfig(SettingType.Float, 42.5);
        
        // Assert - all should use invariant culture (period as decimal separator)
        Assert.Equal("42.5", result1);
        Assert.Equal("42.5", result2);
        Assert.Equal("42.5", result3);
    }
    
    [Fact]
    public void FormatForConfig_String_HandlesSpecialCharacters()
    {
        // Arrange & Act
        var result1 = SettingTypeHelpers.FormatForConfig(SettingType.String, "simple");
        var result2 = SettingTypeHelpers.FormatForConfig(SettingType.String, "with space");
        var result3 = SettingTypeHelpers.FormatForConfig(SettingType.String, "with;semicolon");
        
        // Assert - strings with special characters should be quoted
        Assert.Equal("simple", result1);
        Assert.Equal("\"with space\"", result2);
        Assert.Equal("\"with;semicolon\"", result3);
    }
    
    [Fact]
    public void SafeConvertToBool_HandlesAllTypes()
    {
        // Test through FormatForConfig
        Assert.Equal("true", SettingTypeHelpers.FormatForConfig(SettingType.Bool, true));
        Assert.Equal("true", SettingTypeHelpers.FormatForConfig(SettingType.Bool, "true"));
        Assert.Equal("true", SettingTypeHelpers.FormatForConfig(SettingType.Bool, "1"));
        Assert.Equal("true", SettingTypeHelpers.FormatForConfig(SettingType.Bool, 1));
        Assert.Equal("true", SettingTypeHelpers.FormatForConfig(SettingType.Bool, 1.0f));
        
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, false));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, "false"));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, "0"));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, 0));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, 0.0f));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, null));
        Assert.Equal("false", SettingTypeHelpers.FormatForConfig(SettingType.Bool, "invalid"));
    }
    
    [Fact]
    public void SafeConvertToInt_HandlesAllTypes()
    {
        // Test through FormatForConfig
        Assert.Equal("42", SettingTypeHelpers.FormatForConfig(SettingType.Int, 42));
        Assert.Equal("42", SettingTypeHelpers.FormatForConfig(SettingType.Int, "42"));
        Assert.Equal("42", SettingTypeHelpers.FormatForConfig(SettingType.Int, 42.0f));
        Assert.Equal("1", SettingTypeHelpers.FormatForConfig(SettingType.Int, true));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Int, false));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Int, null));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Int, "invalid"));
    }
    
    [Fact]
    public void SafeConvertToFloat_HandlesAllTypes()
    {
        // Test through FormatForConfig
        Assert.Equal("42.5", SettingTypeHelpers.FormatForConfig(SettingType.Float, 42.5f));
        Assert.Equal("42.5", SettingTypeHelpers.FormatForConfig(SettingType.Float, "42.5"));
        Assert.Equal("42", SettingTypeHelpers.FormatForConfig(SettingType.Float, 42));
        Assert.Equal("1", SettingTypeHelpers.FormatForConfig(SettingType.Float, true));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Float, false));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Float, null));
        Assert.Equal("0", SettingTypeHelpers.FormatForConfig(SettingType.Float, "invalid"));
    }
    
    // Add test for invalid parsing scenarios - should throw exceptions in ParseFromString
    [Fact]
    public void ParseFromString_Int_InvalidInput_ThrowsFormatException()
    {
        Assert.Throws<FormatException>(() => SettingTypeHelpers.ParseFromString(SettingType.Int, "not-a-number"));
    }
    
    [Fact]
    public void ParseFromString_Float_InvalidInput_ThrowsFormatException()
    {
        Assert.Throws<FormatException>(() => SettingTypeHelpers.ParseFromString(SettingType.Float, "not-a-number"));
    }
}
