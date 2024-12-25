import sys
import os
import shutil
import re
from jinja2 import Template
import importlib.util
from typer.main import get_command
import ast
from urllib.request import urlopen

# Import site configuration
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from site_config import SITE_CONFIG

# Base directories
BASE_DIR = "."
STATIC_DIR = ".atrium/docs"  # Output directory for static site
COVER_IMAGE = "cover.png"
MCP_SERVER_PATH = os.path.join(STATIC_DIR, "mcp_server.py")

# Templates
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Atrium</title>
    <link rel="stylesheet" href="style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        h1 {
            text-align: center;
            margin-top: 20px;
            font-size: 2.5em;
            color: #333;
        }
        .grid {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            width: 300px;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background: #fff;
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
            text-align: left;
            padding: 15px;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
        }
        .card img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .card h2 {
            font-size: 1.4em;
            margin: 0 0 10px 0;
            color: #333;
        }
        .card .metadata {
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }
        .card .metadata span {
            display: block;
            margin-bottom: 5px;
        }
        .card p {
            font-size: 0.9em;
            color: #555;
            margin: 10px 0;
        }
        .card a {
            text-decoration: none;
            color: #007BFF;
            font-weight: bold;
            transition: color 0.2s;
        }
        .card a:hover {
            color: #0056b3;
        }
        .external-source {
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <h1>Atrium</h1>
    <div class="grid">
        {% raw %}{% for solution in solutions %}{% endraw %}
        <div class="card">
            {% raw %}{% if solution.cover %}{% endraw %}
            <img src="{{ "{{ solution.cover }}" }}" alt="{{ "{{ solution.name }}" }}">
            {% raw %}{% endif %}{% endraw %}
            <h2><a href="{{ "{{ solution.link }}" }}/index.html">{{ "{{ solution.name }}" }}</a></h2>
            <div class="metadata">
                {% raw %}{% if solution.author %}{% endraw %}
                <span>Author: {{ "{{ solution.author }}" }}</span>
                {% raw %}{% endif %}{% endraw %}
                {% raw %}{% if solution.version %}{% endraw %}
                <span>Version: {{ "{{ solution.version }}" }}</span>
                {% raw %}{% endif %}{% endraw %}
            </div>
            <p>{{ "{{ solution.description }}" }}</p>
            {% raw %}{% if solution.external_source %}{% endraw %}
            <div class="external-source">
                Source: <a href="{{ "{{ solution.external_source }}" }}" target="_blank">{{ "{{ solution.external_source }}" }}</a>
            </div>
            {% raw %}{% endif %}{% endraw %}
        </div>
        {% raw %}{% endfor %}{% endraw %}
    </div>
</body>
</html>
"""

SOLUTION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ "{{ title }}" }}</title>
    <link rel="stylesheet" href="../../style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            width: 80%;
            margin: auto;
            overflow: hidden;
            padding-bottom: 40px;
        }
        header {
            background: #333;
            color: #fff;
            padding: 20px 0;
            margin-bottom: 30px;
        }
        header h1 {
            text-align: center;
            margin: 0;
            font-size: 24px;
        }
        .cover {
            display: block;
            margin: 20px auto;
            max-width: 80%;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .execution-command {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #dee2e6;
        }
        .execution-command code {
            display: block;
            background: #fff;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
            border: 1px solid #e9ecef;
            font-family: monospace;
        }
        .copy-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .copy-button:hover {
            background: #0056b3;
        }
        .metadata-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .metadata-item {
            margin-bottom: 15px;
        }
        .metadata-item h3 {
            margin: 0 0 5px 0;
            color: #495057;
            font-size: 16px;
        }
        .metadata-item p {
            margin: 0;
            color: #6c757d;
        }
        .external-source {
            background: #e9ecef;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .navigation {
            text-align: center;
            margin: 20px 0;
        }
        .navigation a {
            color: #fff;
            text-decoration: none;
            padding: 5px 15px;
            border-radius: 4px;
            transition: opacity 0.2s;
        }
        .navigation a:hover {
            opacity: 0.8;
        }
    </style>
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                const copyButton = document.getElementById('copyButton');
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = 'Copy Command';
                }, 2000);
            });
        }
    </script>
</head>
<body>
    <header>
        <h1>{{ "{{ title }}" }}</h1>
        <div class="navigation">
            <a href="../../index.html">Back to Overview</a>
        </div>
    </header>
    <div class="container">
        {% raw %}{% if cover %}{% endraw %}
        <img src="{{ "{{ cover }}" }}" alt="{{ "{{ title }}" }}" class="cover">
        {% raw %}{% endif %}{% endraw %}

        <div class="execution-command">
            <h2>Run This Script</h2>
            <code>uv run {{ "{{ script_source }}" }}</code>
            <button id="copyButton" class="copy-button" onclick="copyToClipboard('uv run {{ "{{ script_source }}" }}')">
                Copy Command
            </button>
        </div>

        <div class="metadata-section">
            <div class="metadata-grid">
                {% raw %}{% for key, value in metadata.items() %}{% endraw %}
                <div class="metadata-item">
                    <h3>{{ "{{ key }}" }}</h3>
                    <p>{{ "{{ value }}" }}</p>
                </div>
                {% raw %}{% endfor %}{% endraw %}
            </div>
        </div>

        {% raw %}{% if external_source %}{% endraw %}
        <div class="external-source">
            <h3>External Source</h3>
            <p>This script is sourced from: <a href="{{ "{{ external_source }}" }}" target="_blank">{{ "{{ external_source }}" }}</a></p>
        </div>
        {% raw %}{% endif %}{% endraw %}
    </div>
</body>
</html>
"""

def extract_metadata(file_path):
    """Extract metadata from a Python script with robust handling of multiline lists."""
    metadata = {}
    with open(file_path, "r") as f:
        content = f.read()

    # Match metadata block between "# /// script" and "# ///"
    match = re.search(r"# /// script\n(.*?)# ///", content, re.DOTALL)
    if match:
        lines = match.group(1).strip().splitlines()
        key, value = None, None

        for line_no, line in enumerate(lines):
            line = line.strip()
            print(f"Line {line_no + 1}: {line}")  # Debugging: Show the raw line being processed

            # Check for key-value pairs (with =)
            if "=" in line and not (key == "dependencies" and isinstance(value, list)):
                # Save the previous key-value pair
                if key is not None and value is not None:
                    # Remove quotes from string values before saving
                    if isinstance(value, str):
                        value = value.strip('"').strip("'")
                    print(f"Saving metadata: {key} = {value}")  # Debugging
                    metadata[key] = value

                # Parse the new key-value pair
                key, value = map(str.strip, line.split("=", 1))
                key = key.lstrip("# ").strip()
                value = value.strip()

                print(f"New key detected: {key}, Initial value: {value}")  # Debugging

                # Handle special case for dependencies
                if key == "dependencies":
                    if value.startswith("[") and not value.endswith("]"):
                        # Start of a multiline dependencies list
                        value = []
                        print(f"Start of multiline list for {key}")  # Debugging
                    elif value.startswith("[") and value.endswith("]"):
                        # Inline dependencies list
                        try:
                            value = eval(value)  # Parse inline list
                            print(f"Parsed inline dependencies for {key}: {value}")  # Debugging
                        except Exception as e:
                            print(f"Error parsing dependencies list for {key}: {e}")  # Debugging
                            value = []
                elif value.startswith("[") and value.endswith("]"):
                    # Handle general inline lists
                    try:
                        value = eval(value)  # Parse inline list
                        print(f"Parsed inline list for {key}: {value}")  # Debugging
                    except Exception as e:
                        print(f"Error parsing list for {key}: {e}")  # Debugging
                        value = value.strip('"').strip("'")
                elif value.startswith("[") and not value.endswith("]"):
                    # Start of a multiline list for general keys
                    value = []
                    print(f"Start of multiline list for {key}")  # Debugging
            elif key == "dependencies" and isinstance(value, list):
                # Continuation of a multiline dependencies list
                line_content = line.lstrip("# ").strip("[],").strip('"').strip("'")
                if line_content:
                    value.append(line_content)
                    print(f"Appending to {key}: {line_content}")  # Debugging
                if line.endswith("]"):  # End of multiline dependencies list
                    print(f"Completed multiline dependencies list for {key}: {value}")  # Debugging
                    metadata[key] = value
                    key, value = None, None
            elif key and isinstance(value, list) and line.startswith("#"):
                # Continuation of a general multiline list
                line_content = line.lstrip("# ").strip("[],").strip('"').strip("'")
                if line_content:
                    value.append(line_content)
                    print(f"Appending to {key}: {line_content}")  # Debugging
                if line.endswith("]"):  # End of multiline list
                    print(f"Completed multiline list for {key}: {value}")  # Debugging
                    metadata[key] = value
                    key, value = None, None
            elif key and not line.startswith("#"):
                # End of a block or key-value pair
                # Remove quotes from string values before saving
                if isinstance(value, str):
                    value = value.strip('"').strip("'")
                print(f"Saving key: {key} with value: {value}")  # Debugging
                metadata[key] = value
                key, value = None, None

        # Final key-value pair
        if key and value is not None:
            # Remove quotes from string values before saving
            if isinstance(value, str):
                value = value.strip('"').strip("'")
            print(f"Final metadata save: {key} = {value}")  # Debugging
            metadata[key] = value

    # If external_source is present, use it as the script source
    if "external_source" in metadata:
        metadata["script_source"] = metadata["external_source"]
    else:
        metadata["script_source"] = f"{SITE_CONFIG['base_url']}/{file_path}"

    return metadata

    print(f"Metadata extracted from {file_path}: {metadata}")
    return metadata



def copy_files(source_dir, target_dir, extensions=None):
    """Copy files with specific extensions from source to target directory."""
    if extensions is None:
        extensions = []
    os.makedirs(target_dir, exist_ok=True)
    for file_name in os.listdir(source_dir):
        if any(file_name.endswith(ext) for ext in extensions):
            source_path = os.path.join(source_dir, file_name)
            target_path = os.path.join(target_dir, file_name)
            shutil.copy2(source_path, target_path)

def format_metadata(metadata):
    """Format metadata for display in the HTML table."""
    formatted = {}
    for key, value in metadata.items():
        formatted_key = key.replace("_", " ").title()
        if isinstance(value, list):
            # Format lists as bullet points, skipping empty entries
            formatted_value = "<ul>" + "".join(f"<li>{item}</li>" for item in value if item) + "</ul>"
        else:
            formatted_value = value
        formatted[formatted_key] = formatted_value
    return formatted

def generate_sitemap_txt(solutions, static_dir):
    sitemap_path = os.path.join(static_dir, "sitemap.txt")
    with open(sitemap_path, "w") as f:
        for solution in solutions:
            group_name = solution["link"].split("/")[0]
            solution_name = solution["name"]
            description = solution["description"]
            url = f"{SITE_CONFIG['base_url']}/{solution['link']}"
            f.write(f"Group: {group_name}\nName: {solution_name}\nDescription: {description}\nURL: {url}\n\n")


def sanitize_function_name(name):
    """Sanitize a string to make it a valid Python function name."""
    sanitized = re.sub(r"[^0-9a-zA-Z_]", "", name.replace(" ", "_").lower())
    if re.match(r"^\d", sanitized):  # If it starts with a number, prepend an underscore
        sanitized = f"_{sanitized}"
    return sanitized

def extract_typer_commands_with_ast(file_path):
    """
    Extract Typer commands and their arguments using AST.

    Args:
        file_path (str): Path to the Python script containing the Typer app.

    Returns:
        list: List of dictionaries containing command name and arguments.
    """
    commands = []

    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        # Look for function definitions with Typer `@app.command()` decorators
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "command"
                ):
                    # Extract function name
                    command_name = node.name

                    # Extract arguments
                    arguments = []
                    num_args = len(node.args.args)
                    num_defaults = len(node.args.defaults)
                    defaults_start = num_args - num_defaults

                    for i, arg in enumerate(node.args.args):
                        arg_name = arg.arg
                        arg_type = "str"  # Default to `str` if no type annotation
                        default_value = None

                        if arg.annotation:
                            try:
                                arg_type = ast.unparse(arg.annotation)
                            except Exception:
                                arg_type = "str"  # Fallback to `str` if parsing fails

                        # Match argument with default if within range
                        if i >= defaults_start:
                            try:
                                default_index = i - defaults_start
                                default_value = ast.literal_eval(node.args.defaults[default_index])
                            except Exception:
                                default_value = None  # Fallback if evaluation fails

                        arguments.append({
                            "name": arg_name,
                            "type": arg_type,
                            "default": default_value,
                        })

                    commands.append({
                        "command_name": command_name,
                        "arguments": arguments,
                    })

    return commands

def generate_mcp_tool_definitions_with_ast(solutions):
    tool_definitions = []
    base_url = SITE_CONFIG['base_url']

    for solution in solutions:
        if 'external_source' in solution and solution['external_source']:
            solution_name = os.path.basename(os.path.dirname(solution['link']))
            sanitized_function_name = sanitize_function_name(solution_name)
            
            tool_definition = f'''
@mcp.tool()
def {sanitized_function_name}_run():
    """
    Run external script: {solution['name']}
    
    This script is sourced from: {solution['external_source']}
    """
    import subprocess
    import threading
    import tempfile
    import urllib.request
    
    def run_command():
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            try:
                urllib.request.urlretrieve('{solution['external_source']}', tmp.name)
                command = f"uv run {{tmp.name}}"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Command failed with error: {{result.stderr}}")
                else:
                    print(f"Command output: {{result.stdout.strip()}}")
            finally:
                os.unlink(tmp.name)
    
    thread = threading.Thread(target=run_command, daemon=True)
    thread.start()
    return "Command is running in the background."
'''
            tool_definitions.append(tool_definition)
            continue

        solution_dir = os.path.dirname(solution["uv_command"].replace(f"{base_url}/", ""))
        solution_path = os.path.join(BASE_DIR, solution_dir)
        
        if not os.path.exists(solution_path):
            print(f"Directory not found: {solution_path}. Skipping.")
            continue

        python_files = sorted(
            [f for f in os.listdir(solution_path) if f.endswith(".py")],
            reverse=True,
        )
        if not python_files:
            print(f"No Python files found in {solution_path}. Skipping.")
            continue

        latest_python_file = os.path.join(solution_path, python_files[0])
        
        try:
            metadata = extract_metadata(latest_python_file)
            script_title = metadata.get("title", "Untitled Script")
            script_description = metadata.get("description", "No description provided.")

            solution_name = os.path.basename(solution_dir)
            sanitized_function_name = sanitize_function_name(solution_name)

            typer_commands = extract_typer_commands_with_ast(latest_python_file)

            for command in typer_commands:
                command_name = command["command_name"]
                args_str = ", ".join(
                    f"{arg['name']}: {arg['type']} = {repr(arg['default'])}" if arg["default"] is not None
                    else f"{arg['name']}: {arg['type']}"
                    for arg in command["arguments"]
                )
                args_cmd_str = " ".join(
                    f"--{arg['name']} {{{arg['name']}}}"
                    for arg in command["arguments"]
                )
                
                tool_definition = f'''
@mcp.tool()
def {sanitized_function_name}_{command_name}({args_str}):
    """{script_title}

    {script_description}"""
    import subprocess
    import threading

    def run_command():
        command = f"uv run {solution['uv_command']} {args_cmd_str}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed with error: {{result.stderr}}")
        else:
            print(f"Command output: {{result.stdout.strip()}}")

    thread = threading.Thread(target=run_command, daemon=True)
    thread.start()
    return "Command is running in the background."
'''
                tool_definitions.append(tool_definition)
        except Exception as e:
            print(f"Error processing {latest_python_file}: {e}")
            continue

    return "\n".join(tool_definitions)

def download_external_script(url, output_path, original_metadata):
    """Download external script and preserve original metadata."""
    with urlopen(url) as response:
        content = response.read().decode('utf-8')
        with open(output_path, 'w') as f:
            f.write(content)

def generate_static_site(base_dir, static_dir):
    os.makedirs(static_dir, exist_ok=True)
    solutions = []

    for entry in os.scandir(base_dir):
        if entry.is_dir() and not entry.name.startswith(".") and entry.name != "docs":
            group_path = os.path.join(static_dir, entry.name)
            os.makedirs(group_path, exist_ok=True)

            for solution_entry in os.scandir(entry.path):
                if solution_entry.is_dir():
                    solution_name = solution_entry.name
                    solution_files = sorted(
                        [f for f in os.listdir(solution_entry.path) if f.endswith(".py")],
                        reverse=True,
                    )
                    if not solution_files:
                        continue

                    most_recent_file = solution_files[0]
                    file_path = os.path.join(solution_entry.path, most_recent_file)
                    metadata = extract_metadata(file_path)

                    solution_output = os.path.join(group_path, solution_name)
                    os.makedirs(solution_output, exist_ok=True)

                    # Handle external scripts
                    if "external_source" in metadata:
                        output_path = os.path.join(solution_output, most_recent_file)
                        try:
                            with urlopen(metadata["external_source"]) as response:
                                external_content = response.read().decode('utf-8')
                                with open(output_path, 'w') as f:
                                    f.write(external_content)
                        except Exception as e:
                            print(f"Error downloading external script: {e}")

                    # Copy local files
                    copy_files(solution_entry.path, solution_output, extensions=[".py", ".png"])

                    cover_relative_path = (
                        f"{entry.name}/{solution_name}/{COVER_IMAGE}"
                        if os.path.exists(os.path.join(solution_entry.path, COVER_IMAGE))
                        else None
                    )
                    cover_solution_page = COVER_IMAGE if os.path.exists(os.path.join(solution_entry.path, COVER_IMAGE)) else None

                    base_url = SITE_CONFIG['base_url']
                    script_source = metadata.get("external_source", f"{base_url}/{entry.name}/{solution_name}/{most_recent_file}")
                    
                    solution_metadata = {
                        "name": metadata.get("title", solution_name),
                        "description": metadata.get("description", "No description provided."),
                        "link": f"{entry.name}/{solution_name}",
                        "cover": cover_relative_path,
                        "author": metadata.get("author", ""),
                        "version": metadata.get("version", ""),
                        "external_source": metadata.get("external_source", ""),
                        "uv_command": script_source,
                    }

                    # Generate solution page
                    with open(os.path.join(solution_output, "index.html"), "w") as f:
                        f.write(Template(SOLUTION_TEMPLATE).render(
                            title=solution_metadata["name"],
                            cover=cover_solution_page,
                            metadata=format_metadata(metadata),
                            external_source=solution_metadata["external_source"],
                            script_source=script_source,
                            site_config=SITE_CONFIG
                        ))
                    solutions.append(solution_metadata)

    # Generate index page
    with open(os.path.join(static_dir, "index.html"), "w") as f:
        f.write(Template(INDEX_TEMPLATE).render(solutions=solutions, site_config=SITE_CONFIG))
    
    generate_sitemap_txt(solutions, static_dir)
    
    tool_definitions = generate_mcp_tool_definitions_with_ast(solutions)
    with open(MCP_SERVER_PATH, "w") as f:
        f.write(Template("""
from fastmcp import FastMCP
from typing import Optional, List, Union
import subprocess

mcp = FastMCP("Demo 🚀")

{{ "{{ tool_definitions }}" }}

if __name__ == "__main__":
    mcp.run()
""").render(tool_definitions=tool_definitions))
    print(f"mcp_server.py generated at {MCP_SERVER_PATH}")

if __name__ == "__main__":
    generate_static_site(BASE_DIR, STATIC_DIR)
