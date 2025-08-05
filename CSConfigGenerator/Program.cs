using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using CSConfigGenerator;
using CSConfigGenerator.Interfaces;
using CSConfigGenerator.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Scoped services
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddScoped<ISchemaService, SchemaService>();
builder.Services.AddScoped<IPresetService, PresetService>();
builder.Services.AddScoped<ILocalStorageService, LocalStorageService>();
builder.Services.AddScoped<IUserConfigService, UserConfigService>();
builder.Services.AddScoped<IToastService, ToastService>();
builder.Services.AddScoped<IConfigStateService, ConfigStateService>();

// Initialize services
var host = builder.Build();
var schemaService = host.Services.GetRequiredService<ISchemaService>();
await schemaService.InitializeAsync();

var configStateService = host.Services.GetRequiredService<IConfigStateService>();
configStateService.InitializeDefaults();

await host.RunAsync();
