# Environment Setup

This is a Blazor standalone WASM project.

## .NET Core SDK Installation

To build and test this project, you will need to install the .NET Core SDK.

```bash
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x ./dotnet-install.sh
./dotnet-install.sh --channel 9.0
```

## Environment variables

After installation, you need to add the `.dotnet` directory to your path.

```bash
export PATH=$PATH:$HOME/.dotnet
```

## Build and Test

Once the SDK is installed and configured, you can build and test the project using the following commands:

```bash
dotnet build
dotnet test
```
