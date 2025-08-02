# cs-config-generator
A web-based config generator for Counter-Strike 2.

## Development

This project uses `pre-commit` to enforce consistent code formatting for .NET files. To get started, you'll need to install the pre-commit hooks.

### Initial Setup

1.  **Install `pre-commit`**.
    *   Follow the official installation guide: [https://pre-commit.com/#install](https://pre-commit.com/#install)

2.  **Install the pre-commit hooks**.
    *   Run the following command in the root of the repository:
        ```bash
        pre-commit install
        ```

### Usage

Once installed, the pre-commit hooks will run automatically every time you make a commit. They will check for formatting issues in C# and Razor files.

If a hook finds an issue, it will report it and your commit will be aborted. You will need to run `dotnet format` to fix the issues, then `git add` the changes and try committing again.

You can also run the hooks manually on all files at any time:

```bash
pre-commit run --all-files
```
