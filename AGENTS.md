# Project Context

## Overview

Blazor WebAssembly application for Counter-Strike 2 console command reference. Deployed to GitHub Pages.

**Tech Stack:**
- .NET 9.0 Blazor WASM (standalone)
- Bootstrap 5 + Bootstrap Icons

## Setup

Install .NET 9.0 SDK:
```bash
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x ./dotnet-install.sh
./dotnet-install.sh --channel 9.0
export PATH=$PATH:$HOME/.dotnet
```

Build/Test:
```bash
dotnet build
dotnet test
```

## Coding Standards

**CSS Units:** Prefer `rem` (global sizing) and `em` (component-relative) over `px` (use only for borders/fixed elements).

