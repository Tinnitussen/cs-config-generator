#!/bin/sh
set -eu
dotnet-format --check --include "$@"
