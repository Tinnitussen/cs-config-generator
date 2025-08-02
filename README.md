# cs-config-generator
A web-based config generator for Counter-Strike 2.

## Development

This project uses `pre-commit` to enforce consistent code formatting. To get started, you'll need to install the pre-commit hooks.

### Initial Setup

1.  **Install `pre-commit`**.
    *   Follow the official installation guide: [https://pre-commit.com/#install](https://pre-commit.com/#install)
    *   For most Python users, `pip install pre-commit` is sufficient.

2.  **Install the pre-commit hooks**.
    *   Run the following command in the root of the repository:
        ```bash
        pre-commit install
        ```

### Usage

Once installed, the pre-commit hooks will run automatically every time you make a commit. They will check for formatting issues and, in some cases, fix them automatically.

If a hook makes a change, your commit will be aborted. Simply review the changes and `git add` them to your commit, then try committing again.

You can also run the hooks manually on all files at any time:

```bash
pre-commit run --all-files
```
