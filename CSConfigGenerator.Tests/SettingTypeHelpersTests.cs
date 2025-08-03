using System.Globalization;
using System.Text.Json;
using CSConfigGenerator.Models;
using Xunit;

namespace CSConfigGenerator.Tests
{
    public class SettingTypeHelpersTests
    {
        [Theory]
        [InlineData(SettingType.Bool, "true", true)]
        [InlineData(SettingType.Bool, "false", false)]
        [InlineData(SettingType.Bool, "1", true)]
        [InlineData(SettingType.Bool, "0", false)]
        [InlineData(SettingType.Int, "123", 123)]
        [InlineData(SettingType.Float, "123.45", 123.45f)]
        [InlineData(SettingType.String, "hello", "hello")]
        [InlineData(SettingType.Enum, "1", "1")]
        [InlineData(SettingType.Enum, "sv_cheats", "sv_cheats")]
        [InlineData(SettingType.Bitmask, "2", 2)]
        [InlineData(SettingType.UnknownNumeric, "99.9", 99.9f)]
        [InlineData(SettingType.UnknownInteger, "789", 789)]
        [InlineData(SettingType.Action, "my_action", "my_action")]
        public void ParseFromString_ShouldReturnCorrectType(SettingType type, string input, object expected)
        {
            // Act
            var result = SettingTypeHelpers.ParseFromString(type, input);

            // Assert
            Assert.Equal(expected, result);
        }

        [Theory]
        [InlineData(SettingType.Bool, true, "true")]
        [InlineData(SettingType.Bool, false, "false")]
        [InlineData(SettingType.Int, 123, "123")]
        [InlineData(SettingType.Float, 123.45f, "123.45")]
        [InlineData(SettingType.String, "hello", "hello")]
        [InlineData(SettingType.String, "hello world", "\"hello world\"")]
        [InlineData(SettingType.String, "hello;world", "\"hello;world\"")]
        [InlineData(SettingType.Enum, "some_enum_val", "some_enum_val")]
        [InlineData(SettingType.Bitmask, 2, "2")]
        [InlineData(SettingType.UnknownNumeric, 99.9f, "99.9")]
        [InlineData(SettingType.UnknownInteger, 789, "789")]
        [InlineData(SettingType.Action, "my_action", "my_action")]
        public void FormatForConfig_ShouldReturnCorrectString(SettingType type, object value, string expected)
        {
            // Act
            var result = SettingTypeHelpers.FormatForConfig(type, value);

            // Assert
            Assert.Equal(expected, result);
        }

        [Theory]
        [InlineData(SettingType.Bool, false)]
        [InlineData(SettingType.Int, 0)]
        [InlineData(SettingType.Float, 0.0f)]
        [InlineData(SettingType.String, "")]
        [InlineData(SettingType.Enum, "")]
        [InlineData(SettingType.Bitmask, 0)]
        [InlineData(SettingType.UnknownNumeric, 0.0f)]
        [InlineData(SettingType.UnknownInteger, 0)]
        [InlineData(SettingType.Action, "")]
        public void GetDefaultValue_ShouldReturnCorrectDefault(SettingType type, object expected)
        {
            // Act
            var result = SettingTypeHelpers.GetDefaultValue(type);

            // Assert
            Assert.Equal(expected, result);
        }

        [Theory]
        [InlineData(SettingType.Bool, true, true)]
        [InlineData(SettingType.Bool, "true", true)]
        [InlineData(SettingType.Bool, 1, true)]
        [InlineData(SettingType.Bool, "1", true)]
        [InlineData(SettingType.Bool, false, false)]
        [InlineData(SettingType.Bool, "false", false)]
        [InlineData(SettingType.Bool, 0, false)]
        [InlineData(SettingType.Bool, "0", false)]
        [InlineData(SettingType.Int, 123, 123)]
        [InlineData(SettingType.Int, "123", 123)]
        [InlineData(SettingType.Float, 123.45f, 123.45f)]
        [InlineData(SettingType.Float, "123.45", 123.45f)]
        [InlineData(SettingType.String, "hello", "hello")]
        [InlineData(SettingType.Enum, "some_enum_val", "some_enum_val")]
        [InlineData(SettingType.Bitmask, 2, 2)]
        [InlineData(SettingType.UnknownNumeric, 99.9f, 99.9f)]
        [InlineData(SettingType.UnknownInteger, 789, 789)]
        [InlineData(SettingType.Action, "my_action", "my_action")]
        public void ConvertToType_ShouldReturnCorrectType(SettingType type, object input, object expected)
        {
            // Act
            var result = SettingTypeHelpers.ConvertToType(type, input);

            // Assert
            Assert.Equal(expected, result);
        }

        [Fact]
        public void ConvertFromJson_ShouldReturnCorrectType()
        {
            // Arrange
            var jsonBool = JsonSerializer.SerializeToElement(true);
            var jsonInt = JsonSerializer.SerializeToElement(123);
            var jsonFloat = JsonSerializer.SerializeToElement(123.45f);
            var jsonString = JsonSerializer.SerializeToElement("hello");

            // Act & Assert
            Assert.True((bool)SettingTypeHelpers.ConvertFromJson(SettingType.Bool, jsonBool));
            Assert.Equal(123, (int)SettingTypeHelpers.ConvertFromJson(SettingType.Int, jsonInt));
            Assert.Equal(123.45f, (float)SettingTypeHelpers.ConvertFromJson(SettingType.Float, jsonFloat));
            Assert.Equal("hello", (string)SettingTypeHelpers.ConvertFromJson(SettingType.String, jsonString));
            Assert.Equal(123, (int)SettingTypeHelpers.ConvertFromJson(SettingType.Bitmask, jsonInt));
            Assert.Equal(123.45f, (float)SettingTypeHelpers.ConvertFromJson(SettingType.UnknownNumeric, jsonFloat));
            Assert.Equal(123, (int)SettingTypeHelpers.ConvertFromJson(SettingType.UnknownInteger, jsonInt));
            Assert.Equal("hello", (string)SettingTypeHelpers.ConvertFromJson(SettingType.Action, jsonString));
        }

        [Fact]
        public void ParseFromString_WithInvariantCulture()
        {
            // Arrange
            var originalCulture = CultureInfo.CurrentCulture;
            CultureInfo.CurrentCulture = new CultureInfo("fr-FR"); // A culture that uses "," as decimal separator

            // Act
            var result = SettingTypeHelpers.ParseFromString(SettingType.Float, "123.45");

            // Cleanup
            CultureInfo.CurrentCulture = originalCulture;

            // Assert
            Assert.Equal(123.45f, result);
        }
    }
}
