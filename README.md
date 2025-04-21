# Fal AI MCP Server

An MCP (Model Context Protocol) server to use the fal.ai APIs to generate images and videos.
This is a barebones server that anyone can extend to use different fal.ai models and API endpoints.

## Usage

Install [uv](https://docs.astral.sh/uv/) and add the server to an MCP config using `uvx`:

```json
{
    "name": "fal-ai-mcp-server",
    "command": "uvx",
    "args": [
        "fal-ai-mcp-server"
    ],
    "env": {
        "FAL_KEY": "your-key",
        "SAVE_MEDIA_DIR": "path/to/save/images"
    }
}
```

or clone the repo and use `uv` with a directory:

```json
{
    "name": "fal-ai-mcp-server",
    "command": "uv",
    "args": [
        "--directory",
        "path/to/root/dir/",
        "run",
        "main.py"
    ],
    "env": {
        "FAL_KEY": "your-key",
        "SAVE_MEDIA_DIR": "path/to/save/images"
    }
}
```

## Development

### Testing

Clone the repo and use [mcp-client-for-testing](https://github.com/piebro/mcp-client-for-testing) to test the tools of the server.

```bash
uvx mcp-client-for-testing \
    --config '
    [
        {
            "name": "fal-ai-mcp-server",
            "command": "uv",
            "args": [
                "--directory", 
                "path/to/root/dir/", 
                "run", 
                "main.py"
            ],
            "env": {
                "FAL_KEY": "your-key",
                "SAVE_MEDIA_DIR": "path/to/save/images"
            }
        }
    ]
    ' \
    --tool_call '{"name": "echo_tool", "arguments": {"message": "Hello, world!"}}'
```

### Formatting and Linting

The code is formatted and linted with ruff:

```bash
uv run ruff format
uv run ruff check --fix
```

### Building with uv

Build the package using uv:

```bash
uv build
```

### Releasing a New Version

To release a new version of the package to PyPI, create and push a new Git tag:

1. Checkout the main branch and get the current version:
   ```bash
   git checkout main
   git pull origin main
   git describe --tags
   ```

2. Create and push a new Git tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

The GitHub Actions workflow will automatically build and publish the package to PyPI when a new tag is pushed.
The python package version number will be derived directly from the Git tag.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.