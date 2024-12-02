# {{ project_name }}

{{ project_description }}

## Usage

Scripts in this repository can be run using UV:

```bash
uv run https://{{ github_username }}.github.io/{{ project_name }}/[group]/[solution]/[version].py
```

## Structure

- Each directory in the root represents a group of related scripts
- Within each group directory are solution directories
- Each solution directory contains versioned Python files

## Contributing

1. Create a new directory under an appropriate group (or create a new group)
2. Add your script with proper metadata (see example below)
3. Submit a pull request

## Example Script Metadata

```python
# /// script
# title = "Script Title"
# description = "Script description"
# author = "Your Name <your.email@example.com>"
# license = "MIT"
# version = "0.1.0"
# keywords = ["keyword1", "keyword2"]
# repository = "https://github.com/username/repository"
# dependencies = [
#     "package1>=1.0.0",
#     "package2>=2.0.0"
# ]
# ///
```

## License

MIT License