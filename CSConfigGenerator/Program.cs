using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using CSConfigGenerator;
using CSConfigGenerator.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Scoped services
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });

// Singleton services
builder.Services.AddScoped<ConfigStateService>();
builder.Services.AddScoped<SchemaService>();

var host = builder.Build();

var schemaService = host.Services.GetRequiredService<SchemaService>();
await schemaService.InitializeAsync();

var configStateService = host.Services.GetRequiredService<ConfigStateService>();
configStateService.InitializeDefaultValues();

await host.RunAsync();