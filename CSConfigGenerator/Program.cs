using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using CSConfigGenerator;
using CSConfigGenerator.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Scoped services
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddScoped<ISchemaService, SchemaService>();
builder.Services.AddScoped<IConfigStateService, ConfigStateService>();
builder.Services.AddScoped<ToastService>();

// Initialize services
var host = builder.Build();
var schemaService = host.Services.GetRequiredService<ISchemaService>();
var configStateService = host.Services.GetRequiredService<IConfigStateService>();

await schemaService.InitializeAsync();
configStateService.InitializeDefaults();

await host.RunAsync();