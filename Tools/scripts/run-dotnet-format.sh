#!/bin/sh
set -eu
cd "$(git rev-parse --show-toplevel)"
dotnet-format CSConfigGenerator.slnx --check --include "$@"
