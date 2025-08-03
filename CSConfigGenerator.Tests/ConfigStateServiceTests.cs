using System.Text.Json;
using CSConfigGenerator.Interfaces;
using CSConfigGenerator.Models;
using CSConfigGenerator.Services;
using Moq;
using Xunit;

namespace CSConfigGenerator.Tests
{
    public class ConfigStateServiceTests
    {
        private readonly Mock<ISchemaService> _mockSchemaService;
        private readonly PlayerConfigStateService _configStateService;
        private readonly List<ConfigSection> _testSections;

        public ConfigStateServiceTests()
        {
            _mockSchemaService = new Mock<ISchemaService>();

            // Create some test command definitions
            var commands = new List<CommandDefinition>
            {
                new() {
                    Command = "sensitivity",
                    ConsoleData = new ConsoleData { DefaultValue = "2.5", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Sensitivity", Type = SettingType.Float, DefaultValue = JsonSerializer.SerializeToElement(2.5f), HideFromDefaultView = false }
                },
                new() {
                    Command = "cl_crosshaircolor",
                    ConsoleData = new ConsoleData { DefaultValue = "1", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Crosshair Color", Type = SettingType.Int, DefaultValue = JsonSerializer.SerializeToElement(1), HideFromDefaultView = false }
                },
                new() {
                    Command = "cl_crosshairdot",
                    ConsoleData = new ConsoleData { DefaultValue = "false", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Crosshair Dot", Type = SettingType.Bool, DefaultValue = JsonSerializer.SerializeToElement(false), HideFromDefaultView = false }
                }
            };

            _testSections =
            [
                new ConfigSection
                {
                    Name = "test_section",
                    DisplayName = "Test Section",
                    Commands = commands
                }
            ];

            // Setup the mock schema service
            _mockSchemaService.Setup(s => s.PlayerSections).Returns(_testSections);
            _mockSchemaService.Setup(s => s.GetPlayerCommand(It.IsAny<string>()))
                .Returns<string>(name => commands.FirstOrDefault(c => c.Command == name));

            _configStateService = new PlayerConfigStateService(_mockSchemaService.Object);
        }

        [Fact]
        public void InitializeDefaults_ShouldLoadSettingsFromSchema()
        {
            // Act
            _configStateService.InitializeDefaults();

            // Assert
            Assert.Equal(_testSections.SelectMany(s => s.Commands).Count(), _configStateService.Settings.Count);

            var setting = _configStateService.GetSetting("sensitivity");
            Assert.NotNull(setting);
            Assert.Equal(2.5f, setting.Value);
        }

        [Fact]
        public void ResetToDefaults_ShouldRestoreDefaultValues()
        {
            // Arrange
            _configStateService.InitializeDefaults();
            var setting = _configStateService.GetSetting("sensitivity");
            _configStateService.SetValue("sensitivity", 999.0f);

            // Act
            _configStateService.ResetToDefaults();

            // Assert
            var resetSetting = _configStateService.GetSetting("sensitivity");
            Assert.Equal(2.5f, resetSetting.Value);
        }

        [Fact]
        public void SetValue_ShouldUpdateSettingValue()
        {
            // Arrange
            _configStateService.InitializeDefaults();
            var commandName = "sensitivity";
            var newValue = 5.0f;

            // Act
            _configStateService.SetValue(commandName, newValue);

            // Assert
            var setting = _configStateService.GetSetting(commandName);
            Assert.Equal(newValue, setting.Value);
        }

        [Fact]
        public void SetIncluded_ShouldUpdateInclusionStatus()
        {
            // Arrange
            _configStateService.InitializeDefaults();
            var commandName = "sensitivity";
            var setting = _configStateService.GetSetting(commandName);
            var originalStatus = setting.IsInConfigEditor;

            // Act
            _configStateService.SetIncluded(commandName, !originalStatus);

            // Assert
            var updatedSetting = _configStateService.GetSetting(commandName);
            Assert.NotEqual(originalStatus, updatedSetting.IsInConfigEditor);
        }

        [Fact]
        public void GenerateConfigFile_ShouldProduceCorrectString()
        {
            // Arrange
            _configStateService.InitializeDefaults();
            _configStateService.SetValue("cl_crosshaircolor", 4);
            _configStateService.SetIncluded("cl_crosshaircolor", true);
            _configStateService.SetValue("sensitivity", 2.5f);
            _configStateService.SetIncluded("sensitivity", true);
            _configStateService.SetIncluded("cl_crosshairdot", false); // Ensure this is not in the config

            // Act
            var configFileContent = _configStateService.GenerateConfigFile();

            // Assert
            Assert.Contains("// Generated by CS Config Generator", configFileContent);
            Assert.Contains("// Player Configuration", configFileContent);
            Assert.Contains("cl_crosshaircolor 4", configFileContent);
            Assert.Contains("sensitivity 2.5", configFileContent);
            Assert.DoesNotContain("cl_crosshairdot", configFileContent);
        }

        [Fact]
        public void ParseConfigFile_ShouldUpdateSettings()
        {
            // Arrange
            _configStateService.InitializeDefaults();
            var configText = "sensitivity 1.23\ncl_crosshaircolor 5";

            // Act
            _configStateService.ParseConfigFile(configText);

            // Assert
            Assert.Equal(1.23f, _configStateService.GetSetting("sensitivity").Value);
            Assert.Equal(5, _configStateService.GetSetting("cl_crosshaircolor").Value);
            Assert.True(_configStateService.GetSetting("sensitivity").IsInConfigEditor);
            Assert.True(_configStateService.GetSetting("cl_crosshaircolor").IsInConfigEditor);
            Assert.False(_configStateService.GetSetting("cl_crosshairdot").IsInConfigEditor);
        }

        [Theory]
        [InlineData("sensitivity", "3.14", true, 3.14f)]
        [InlineData("cl_crosshaircolor", "3", true, 3)]
        [InlineData("cl_crosshairdot", "true", true, true)]
        [InlineData("sensitivity", "invalid-float", false, null)]
        [InlineData("cl_crosshaircolor", "invalid-int", false, null)]
        [InlineData("cl_crosshairdot", "invalid-bool", false, null)]
        [InlineData("non_existent_command", "123", false, null)]
        public void TrySetValueFromString_ShouldWorkAsExpected(string command, string value, bool expectedSuccess, object? expectedValue)
        {
            // Arrange
            _configStateService.InitializeDefaults();

            // Act
            var (isSuccess, errorMessage) = _configStateService.TrySetValueFromString(command, value);

            // Assert
            Assert.Equal(expectedSuccess, isSuccess);

            if (expectedSuccess)
            {
                Assert.Null(errorMessage);
                var setting = _configStateService.GetSetting(command);
                Assert.Equal(expectedValue, setting.Value);
            }
            else
            {
                Assert.NotNull(errorMessage);
            }
        }
    }
}
