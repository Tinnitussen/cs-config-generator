using System;
using System.Text.Json;
using CSConfigGenerator.Models;
using Xunit;

namespace CSConfigGenerator.Tests
{
    public class SettingTypeJsonConverterTests
    {
        private readonly JsonSerializerOptions _options;

        public SettingTypeJsonConverterTests()
        {
            _options = new JsonSerializerOptions();
            _options.Converters.Add(new SettingTypeJsonConverter());
        }

        [Theory]
        [InlineData(SettingType.Bool, "\"bool\"")]
        [InlineData(SettingType.Int, "\"int\"")]
        [InlineData(SettingType.Float, "\"float\"")]
        [InlineData(SettingType.String, "\"string\"")]
        [InlineData(SettingType.Enum, "\"enum\"")]
        [InlineData(SettingType.Bitmask, "\"bitmask\"")]
        [InlineData(SettingType.UnknownNumeric, "\"unknown_numeric\"")]
        [InlineData(SettingType.UnknownInteger, "\"unknown_integer\"")]
        [InlineData(SettingType.Action, "\"action\"")]
        public void Write_ShouldSerializeCorrectly(SettingType type, string expectedJson)
        {
            // Act
            var json = JsonSerializer.Serialize(type, _options);

            // Assert
            Assert.Equal(expectedJson, json);
        }

        [Theory]
        [InlineData("\"bool\"", SettingType.Bool)]
        [InlineData("\"int\"", SettingType.Int)]
        [InlineData("\"float\"", SettingType.Float)]
        [InlineData("\"string\"", SettingType.String)]
        [InlineData("\"enum\"", SettingType.Enum)]
        [InlineData("\"bitmask\"", SettingType.Bitmask)]
        [InlineData("\"unknown_numeric\"", SettingType.UnknownNumeric)]
        [InlineData("\"unknown_integer\"", SettingType.UnknownInteger)]
        [InlineData("\"action\"", SettingType.Action)]
        public void Read_ShouldDeserializeCorrectly(string json, SettingType expectedType)
        {
            // Act
            var type = JsonSerializer.Deserialize<SettingType>(json, _options);

            // Assert
            Assert.Equal(expectedType, type);
        }

        [Fact]
        public void Read_ShouldThrowJsonException_ForUnknownValue()
        {
            // Arrange
            var json = "\"unknown_type\"";

            // Act & Assert
            Assert.Throws<JsonException>(() => JsonSerializer.Deserialize<SettingType>(json, _options));
        }

        [Fact]
        public void Write_ShouldThrowArgumentException_ForInvalidEnumValue()
        {
            // Arrange
            var invalidType = (SettingType)999; // An invalid enum value

            // Act & Assert
            Assert.Throws<ArgumentException>(() => JsonSerializer.Serialize(invalidType, _options));
        }
    }
}
