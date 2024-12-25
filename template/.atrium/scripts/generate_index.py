import sys
import os
import shutil
import re
from jinja2 import Template
import importlib.util
from typer.main import get_command
import ast

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
            text-align: center;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
        }
        .card img {
            width: 100%;
            height: auto;
            border-bottom: 1px solid #ddd;
        }
        .card h2 {
            font-size: 1.6em;
            margin: 15px 10px 5px;
            color: #333;
        }
        .card .author {
            font-size: 1em;
            color: #666;
            margin: 5px 0;
        }
        .card p {
            font-size: 0.9em;
            color: #555;
            margin: 10px 15px 20px;
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
            <h2><a href="{{ "{{ solution.link }}" }}">{{ "{{ solution.name }}" }}</a></h2>
            <p>{{ "{{ solution.description }}" }}</p>
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
        }
        header {
            background: #333;
            color: #fff;
            padding-top: 10px;
            min-height: 70px;
            border-bottom: #0779e4 3px solid;
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
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .metadata {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .instructions {
            background: #eef7ff;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .instructions code {
            display: inline-block;
            background: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            margin-right: 10px;
        }
        .copy-icon {
            cursor: pointer;
            padding: 5px;
            background: #007BFF;
            color: white;
            border-radius: 3px;
            font-size: 14px;
            vertical-align: middle;
        }
        a {
            color: #0779e4;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert("Copied to clipboard!");
            });
        }
    </script>
</head>
<body>
    <header>
        <h1>{{ "{{ title }}" }}</h1>
        <p style="text-align: center; margin-top: 10px;">
            <a href="../../index.html">Back to Overview</a>
        </p>
    </header>
    <div class="container">
        {% raw %}{% if cover %}{% endraw %}
        <img src="{{ "{{ cover }}" }}" alt="{{ "{{ title }}" }}" class="cover">
        {% raw %}{% endif %}{% endraw %}

        <div class="instructions">
            <h2>Run This Solution</h2>
            <p>To run this script, use the following command with UV:</p>
            <code>uv run {{ "{{ link }}" }}</code>
            <span class="copy-icon" onclick="copyToClipboard('uv run {{ "{{ link }}" }}')">Copy</span>
        </div>
        <div class="metadata">
            <table>
                {% raw %}{% for key, value in metadata.items() %}{% endraw %}
                <tr>
                    <th>{{ "{{ key }}" }}</th>
                    <td>{{ "{{ value }}" }}</td>
                </tr>
                {% raw %}{% endfor %}{% endraw %}
                <tr>
                    <th><strong>Source File:</strong></th>
                    <td><a href="blob/main/{{ "{{ link }}" }}" target="_blank">View on GitHub</a></td>
                </tr>
            </table>
        </div>
        {% raw %}{% if repository %}{% endraw %}
        <p><strong>Repository:</strong> <a href="{{ "{{ repository }}" }}" target="_blank">{{ "{{ repository }}" }}</a></p>
        {% raw %}{% endif %}{% endraw %}
        <p><strong>Download Python Files:</strong></p>
        <ul>
            {% raw %}{% for file in metadata.files %}{% endraw %}
            <li><a href="{{ "{{ file }}" }}" download>{{ "{{ file }}" }}</a></li>
            {% raw %}{% endfor %}{% endraw %}
        </ul>
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
    """
    Generate mcp.tool definitions based on Typer commands discovered via AST.
    """
    tool_definitions = []
    base_url = SITE_CONFIG['base_url']

    for solution in solutions:
        solution_dir = os.path.dirname(solution["uv_command"].replace(f"{base_url}/", ""))
        solution_path = os.path.join(BASE_DIR, solution_dir)

        python_files = sorted(
            [f for f in os.listdir(solution_path) if f.endswith(".py")],
            reverse=True,
        )
        if not python_files:
            print(f"No Python files found in {solution_path}. Skipping.")
            continue

        latest_python_file = os.path.join(solution_path, python_files[0])

        metadata = extract_metadata(latest_python_file)
        script_title = metadata.get("title", "Untitled Script")
        script_description = metadata.get("description", "No description provided.")

        solution_name = os.path.basename(solution_dir)
        sanitized_function_name = sanitize_function_name(solution_name)

        typer_commands = extract_typer_commands_with_ast(latest_python_file)

        for command in typer_commands:
            command_name = command["command_name"]
            tool_definition = """
{% raw %}
@mcp.tool()
def """ + f"{sanitized_function_name}_{command_name}" + """(""" + ", ".join(
                f"{arg['name']}: {arg['type']} = {repr(arg['default'])}" if arg["default"] is not None
                else f"{arg['name']}: {arg['type']}"
                for arg in command["arguments"]
            ) + """):
    \"\"\"""" + f"{script_title}\n\n    {script_description}" + """\"\"\"
    import subprocess
    import threading

    def run_command():
        command = f"uv run """ + f"{solution['uv_command']}" + " " + " ".join(
                f"--{arg['name']} {{{arg['name']}}}"
                for arg in command["arguments"]
            ) + """\"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed with error: {result.stderr}")
        else:
            print(f"Command output: {result.stdout.strip()}")

    thread = threading.Thread(target=run_command, daemon=True)
    thread.start()
    return "Command is running in the background."
{% endraw %}"""
            tool_definitions.append(tool_definition)

    return "\n".join(tool_definitions)


def generate_static_site(base_dir, static_dir):
    """Generate the static site."""
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
                    metadata = extract_metadata(os.path.join(solution_entry.path, most_recent_file))
                    metadata.pop("files", None)  # Remove the files section

                    sanitized_function_name = sanitize_function_name(solution_name)

                    cover_relative_path = (
                        f"{entry.name}/{solution_name}/{COVER_IMAGE}"
                        if os.path.exists(os.path.join(solution_entry.path, COVER_IMAGE))
                        else None
                    )
                    cover_solution_page = COVER_IMAGE if os.path.exists(os.path.join(solution_entry.path, COVER_IMAGE)) else None

                    base_url = SITE_CONFIG['base_url']
                    solution_metadata = {
                        "name": solution_name,
                        "function_name": sanitized_function_name,
                        "description": metadata.get("description", "No description provided."),
                        "link": f"{entry.name}/{solution_name}/{most_recent_file}",
                        "cover": cover_relative_path,
                        "cover_solution": cover_solution_page,
                        "repository": metadata.get("repository", ""),
                        "author": metadata.get("author", ""),

                        "uv_command": f"{base_url}/{entry.name}/{solution_name}/{most_recent_file}",
                    }

                    # Copy solution files and cover image
                    solution_output = os.path.join(group_path, solution_name)
                    copy_files(solution_entry.path, solution_output, extensions=[".py", ".png"])

                    # Generate solution page with site_config
                    with open(os.path.join(solution_output, "index.html"), "w") as f:
                        f.write(Template(SOLUTION_TEMPLATE).render(
                            title=solution_metadata["name"],
                            cover=solution_metadata["cover_solution"],
                            metadata=format_metadata(metadata),
                            repository=solution_metadata["repository"],
                            link=f"{entry.name}/{solution_name}/{most_recent_file}",
                            site_config=SITE_CONFIG  # Pass site_config here
                        ))
                    solutions.append(solution_metadata)

    # Generate the main index with site_config
    with open(os.path.join(static_dir, "index.html"), "w") as f:
        f.write(Template(INDEX_TEMPLATE).render(
            solutions=solutions,
            site_config=SITE_CONFIG  # Pass site_config here
        ))
    
    # Generate the sitemap.txt
    generate_sitemap_txt(solutions, static_dir)
    
    # Generate the mcp_server.py with enhanced tool definitions
    tool_definitions = generate_mcp_tool_definitions_with_ast(solutions)
    with open(MCP_SERVER_PATH, "w") as f:
        f.write(
            Template(
                """
from fastmcp import FastMCP
from typing import Optional, List, Union  # Commonly used types
import subprocess  # For executing commands

mcp = FastMCP("Demo 🚀")

{{ "{{ tool_definitions }}" }}

if __name__ == "__main__":
    mcp.run()
"""
            ).render(tool_definitions=tool_definitions)
        )
    print(f"mcp_server.py generated at {MCP_SERVER_PATH}")

if __name__ == "__main__":
    generate_static_site(BASE_DIR, STATIC_DIR)
