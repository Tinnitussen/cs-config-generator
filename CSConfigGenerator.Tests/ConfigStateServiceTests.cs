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
        private readonly ConfigStateService _configStateService;
        private readonly List<ConfigSection> _testPlayerSections;
        private readonly List<ConfigSection> _testServerSections;

        public ConfigStateServiceTests()
        {
            _mockSchemaService = new Mock<ISchemaService>();

            // Create some test command definitions
            var playerCommands = new List<CommandDefinition>
            {
                new() {
                    Command = "sensitivity",
                    ConsoleData = new ConsoleData { DefaultValue = "2.5", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Sensitivity", Type = SettingType.Float, DefaultValue = JsonSerializer.SerializeToElement(2.5f) }
                },
                new() {
                    Command = "cl_crosshaircolor",
                    ConsoleData = new ConsoleData { DefaultValue = "1", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Crosshair Color", Type = SettingType.Int, DefaultValue = JsonSerializer.SerializeToElement(1) }
                }
            };

            var serverCommands = new List<CommandDefinition>
            {
                new() {
                    Command = "sv_cheats",
                    ConsoleData = new ConsoleData { DefaultValue = "0", Flags = [], Description = "", SourcedAt = DateTimeOffset.Now},
                    UiData = new UiData { Label = "Enable Cheats", Type = SettingType.Bool, DefaultValue = JsonSerializer.SerializeToElement(false) }
                }
            };

            var allCommands = playerCommands.Concat(serverCommands).ToList();

            _testPlayerSections =
            [
                new ConfigSection
                {
                    Name = "player_section",
                    DisplayName = "Player Section",
                    Commands = playerCommands
                }
            ];

            _testServerSections =
            [
                new ConfigSection
                {
                    Name = "server_section",
                    DisplayName = "Server Section",
                    Commands = serverCommands
                }
            ];

            // Setup the mock schema service
            _mockSchemaService.Setup(s => s.PlayerSections).Returns(_testPlayerSections);
            _mockSchemaService.Setup(s => s.ServerSections).Returns(_testServerSections);
            _mockSchemaService.Setup(s => s.AllCommandsSections).Returns(new List<ConfigSection>());
            _mockSchemaService.Setup(s => s.GetCommand(It.IsAny<string>()))
                .Returns<string>(name => allCommands.FirstOrDefault(c => c.Command == name));

            _configStateService = new ConfigStateService(_mockSchemaService.Object);
        }


        private void PopulateTestSettings()
        {
            _configStateService.InitializeDefaults();
        }

        [Fact]
        public void InitializeDefaults_ShouldLoadSettingsWithInclusionFalse()
        {
            // Act
            _configStateService.InitializeDefaults();

            // Assert
            var expectedCount = _testPlayerSections.SelectMany(s => s.Commands).Count() + _testServerSections.SelectMany(s => s.Commands).Count();
            Assert.Equal(expectedCount, _configStateService.Settings.Count);

            foreach(var setting in _configStateService.Settings.Values)
            {
                Assert.False(setting.IsInConfigEditor);
            }
        }

        [Fact]
        public void ResetToDefaults_ShouldReloadSettingsWithInclusionFalse()
        {
            // Arrange
            PopulateTestSettings();
            _configStateService.SetIncluded("sensitivity", true);

            // Act
            _configStateService.ResetToDefaults();

            // Assert
            var setting = _configStateService.GetSetting("sensitivity");
            Assert.False(setting.IsInConfigEditor);
        }

        [Fact]
        public void SetValue_ShouldUpdateSettingValue()
        {
            // Arrange
            PopulateTestSettings();
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
            PopulateTestSettings();
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
        public void GenerateConfigFile_ShouldProduceCorrectStringForPlayer()
        {
            // Arrange
            PopulateTestSettings();
            _configStateService.SetValue("cl_crosshaircolor", 4);
            _configStateService.SetIncluded("cl_crosshaircolor", true);
            _configStateService.SetValue("sensitivity", 2.5f);
            _configStateService.SetIncluded("sensitivity", true);
            _configStateService.SetIncluded("sv_cheats", false); // Ensure this is not in the player config

            // Act
            var configFileContent = _configStateService.GenerateConfigFile("player");

            // Assert
            Assert.Contains("// Generated by CS Config Generator", configFileContent);
            Assert.Contains("// Player Configuration", configFileContent);
            Assert.Contains("cl_crosshaircolor 4", configFileContent);
            Assert.Contains("sensitivity 2.5", configFileContent);
            Assert.DoesNotContain("sv_cheats", configFileContent);
        }

        [Fact]
        public void ParseConfigFile_ShouldUpdateSettings()
        {
            // Arrange
            PopulateTestSettings();
            var configText = "sensitivity 1.23\nsv_cheats 1";

            // Act
            _configStateService.ParseConfigFile(configText);

            // Assert
            Assert.Equal(1.23f, _configStateService.GetSetting("sensitivity").Value);
            Assert.Equal(true, _configStateService.GetSetting("sv_cheats").Value);
            Assert.True(_configStateService.GetSetting("sensitivity").IsInConfigEditor);
            Assert.True(_configStateService.GetSetting("sv_cheats").IsInConfigEditor);
        }

        [Theory]
        [InlineData("sensitivity", "3.14", true, 3.14f)]
        [InlineData("cl_crosshaircolor", "3", true, 3)]
        [InlineData("sv_cheats", "true", true, true)]
        [InlineData("sensitivity", "invalid-float", false, null)]
        [InlineData("cl_crosshaircolor", "invalid-int", false, null)]
        [InlineData("sv_cheats", "invalid-bool", false, null)]
        [InlineData("non_existent_command", "123", false, null)]
        public void TrySetValueFromString_ShouldWorkAsExpected(string command, string value, bool expectedSuccess, object? expectedValue)
        {
            // Arrange
            PopulateTestSettings();

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
