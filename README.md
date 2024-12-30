# Atrium

A template for creating collections of UV-compatible Python scripts with automatic documentation generation and deployment.

![Screenshot of an atrium repository](./screenshot.png)

## Features

- 🚀 Automatic documentation generation
- 📦 UV-compatible script distribution
- 🔄 GitHub Pages integration
- 🎨 Clean, responsive web interface
- 🛠️ Command-line tool support

## Quick Start

1. Create your atrium:
```bash
uvx copier copy --trust https://github.com/kephale/atrium my-atrium
cd my-atrium
```

2. Configure GitHub Pages:

- Go to repository Settings > Pages
- Set source to GitHub Actions
- Enable `Read and write permissions` under Settings > Actions > General

3. Add your first script:

```bash
mkdir -p examples/my-script
touch examples/my-script/0.1.0.py
```

## Updating an existing `atrium`

Note: this uses the `--trust` flag because of the template.

```
uvx copier update --trust
```

## Script metadata

The following metadata is required in each `uv` script.

```python
# /// script
# title = "Script Title"
# description = "Detailed description"
# author = "Author Name <email@example.com>"
# version = "1.0.0"
# dependencies = [
#     "package1>=1.0.0",
#     "package2>=2.0.0"
# ]
# ///
```

## Purpose

Atrium is intended to be a lightweight way of storing collections of single-file Python scripts. It borrows many ideas from [album](https://album.solutions/), but uses [uv](https://docs.astral.sh/uv/) to handle dependencies and execution, and [typer](https://typer.tiangolo.com/) for CLI support. As a consequence, your code does not require any customizations for Atrium. Any single-file python script designed for uv can be added to your Atrium, then you can extend the metadata in your script to get the UI/web display you'd like.

There are some next steps planned. Feel free to ping me if you're interested!

## Troubleshooting

### Common Issues

1. GitHub Pages not deploying

- Ensure GitHub Actions has required permissions
- Check workflow runs for specific errors

2. Script metadata not parsing

- Verify metadata format matches example
- Check for syntax errors in dependencies list

## Security

- Always be aware of the code you're running
- Scripts are executed in isolated environments
- Dependencies are verified against requirements
- UV provides secure script execution

## License
MIT License - See LICENSE for details
