#!/bin/sh
set -eu
dotnet-format CSConfigGenerator.slnx --check --include "$@"
