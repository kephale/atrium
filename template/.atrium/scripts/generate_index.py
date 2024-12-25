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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ '{{ site_config.project_name }}' }} - UV Script Collection</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1d4ed8;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #3b82f6;
                --secondary-color: #60a5fa;
                --background-color: #0f172a;
                --card-background: #1e293b;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --border-color: #334155;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif;
            background-color: var(--background-color);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 2.5rem 1rem;
            text-align: center;
            color: white;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .search-container {
            margin: 1rem auto 2rem;
            max-width: 600px;
        }

        .search-box {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border-color);
            border-radius: 0.5rem;
            font-size: 1rem;
            background-color: var(--card-background);
            color: var(--text-primary);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }

        .card {
            background: var(--card-background);
            border-radius: 1rem;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: var(--hover-shadow);
        }

        .card-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }

        .card-content {
            padding: 1.5rem;
        }

        .card-title {
            font-size: 1.25rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            text-decoration: none;
        }

        .card-title:hover {
            color: var(--primary-color);
        }

        .card-metadata {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .card-metadata i {
            margin-right: 0.5rem;
        }

        .card-description {
            color: var(--text-secondary);
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }

        .card-source {
            font-size: 0.85rem;
            padding: 0.5rem;
            background-color: var(--background-color);
            border-radius: 0.5rem;
            margin-top: 1rem;
        }

        .card-source a {
            color: var(--primary-color);
            text-decoration: none;
        }

        .card-source a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .header p {
                font-size: 1rem;
            }
        }
        
                .header-banner {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 3rem 1rem;
            text-align: center;
            color: white;
        }

        .header-content {
            max-width: 800px;
            margin: 0 auto;
        }

        .header-title {
            font-size: 3rem;
            margin-bottom: 1rem;
            font-weight: 800;
        }

        .header-subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }

        .header-stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <header class="header-banner">
        <div class="header-content">
            <h1 class="header-title">{{ '{{ site_config.project_name }}' }}</h1>
            <p class="header-subtitle">{{ '{{ site_config.project_description }}' }}</p>
        </div>
    </header>

    <div class="container">
        <div class="search-container">
            <input type="text" id="searchBox" class="search-box" placeholder="Search scripts..." 
                   onkeyup="filterCards()">
        </div>

        <div class="grid" id="scriptsGrid">
            {%- raw -%}
            {% for solution in solutions %}
            <div class="card">
                
                <div class="card-content">
                    <a href="{{ solution.link }}/index.html" class="card-title">
                        <h2>{{ solution.name }}</h2>
                    </a>

                    {% if solution.cover %}
                    <img class="card-image" src="{{ solution.cover }}" alt="{{ solution.name }}">
                    {% endif %}

                    
                    <div class="card-metadata">
                        {% if solution.author %}
                        <p><i class="fas fa-user"></i> {{ solution.author }}</p>
                        {% endif %}
                        {% if solution.version %}
                        <p><i class="fas fa-code-branch"></i> {{ solution.version }}</p>
                        {% endif %}
                    </div>

                    <p class="card-description">{{ solution.description }}</p>

                    <div class="card-source">
                        <a href="{{ solution.script_source }}" target="_blank">View Source</a>
                    </div>
                </div>
            </div>
            {% endfor %}
            {%- endraw -%}
        </div>
    </div>

    <script>
        function filterCards() {
            const searchText = document.getElementById('searchBox').value.toLowerCase();
            const cards = document.getElementsByClassName('card');
            
            Array.from(cards).forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-description').textContent.toLowerCase();
                const shouldShow = title.includes(searchText) || description.includes(searchText);
                card.style.display = shouldShow ? 'block' : 'none';
            });
        }
    </script>
</body>
</html>
"""

SOLUTION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ '{{ title }}' }} - {{ '{{ site_config.project_name }}' }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1d4ed8;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --code-background: #f1f5f9;
            --tag-background: #e2e8f0;
            --hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #3b82f6;
                --secondary-color: #60a5fa;
                --background-color: #0f172a;
                --card-background: #1e293b;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --border-color: #334155;
                --code-background: #1e293b;
                --tag-background: #334155;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--background-color);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 2.5rem 1rem;
            color: white;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .nav-bar {
            background-color: var(--card-background);
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            color: var(--text-secondary);
            text-decoration: none;
            gap: 0.5rem;
            font-size: 0.95rem;
        }

        .back-link:hover {
            color: var(--primary-color);
        }

        .script-section {
            background: var(--card-background);
            border-radius: 1rem;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        }

        .script-header {
            margin-bottom: 2rem;
        }

        .script-title {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
            padding: 1.5rem;
            background: var(--code-background);
            border-radius: 0.5rem;
        }

        .metadata-item {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .metadata-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .metadata-value {
            font-size: 1rem;
            color: var(--text-primary);
            word-break: break-word;
        }

        .tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .tag {
            background: var(--tag-background);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            color: var(--text-primary);
        }

        .command-section {
            background: var(--code-background);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 2rem 0;
            position: relative;
        }

        .command-title {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }

        .command-box {
            background: rgba(0, 0, 0, 0.1);
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            margin-bottom: 0.5rem;
            overflow-x: auto;
        }

        .copy-button {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }

        .copy-button:hover {
            background: var(--secondary-color);
        }

        .description-section {
            margin: 2rem 0;
        }

        .description-content {
            color: var(--text-secondary);
            font-size: 1.1rem;
            line-height: 1.8;
        }

        .dependencies-section {
            margin: 2rem 0;
        }

        .dependencies-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .dependency-item {
            background: var(--code-background);
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            font-family: monospace;
            font-size: 0.9rem;
        }

        .links-section {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .link-item {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }

        .link-item:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .script-section {
                padding: 1.5rem;
            }
            
            .script-title {
                font-size: 1.75rem;
            }
            
            .metadata-grid {
                grid-template-columns: 1fr;
            }
            
            .command-section {
                padding: 1rem;
            }
            
            .copy-button {
                position: static;
                margin-top: 1rem;
                width: 100%;
                justify-content: center;
            }
        }

                .metadata-section {
            background: var(--card-background);
            border-radius: 1rem;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        }

        .metadata-title {
            font-size: 1.2rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }

        .metadata-item {
            padding: 1rem;
            background: var(--code-background);
            border-radius: 0.5rem;
        }

        .metadata-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .metadata-value {
            font-size: 1rem;
            color: var(--text-primary);
            word-break: break-word;
        }

        .tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .tag {
            background: var(--tag-background);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            color: var(--text-primary);
        }

        .cover-image-container {
            margin: 2rem 0;
            width: 100%;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .card-image {
            width: 100%;
            height: auto;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            display: block;  /* Ensure image is block-level */
            margin: 0 auto;  /* Center the image */
        }

        @media (prefers-color-scheme: dark) {
            .card-image {
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
            }
        }        
    </style>
</head>
<body>
    <header class="header">
        <h1>{{ '{{ title }}' }}</h1>
    </header>

    <nav class="nav-bar">
        <div class="container">
            <a href="../../index.html" class="back-link">
                <i class="fas fa-arrow-left"></i>
                Back to Scripts
            </a>
        </div>
    </nav>

    <main class="container">
        <section class="script-section">
            <div class="script-header">
                <h1 class="script-title">{{ '{{ title }}' }}</h1>
                
                {%- raw -%}
                {% if cover_image %}
                <div class="cover-image-container">
                    <img src="{{ cover_image }}" alt="{{ title }} cover image" class="card-image">
                </div>
                {% endif %}
                {%- endraw -%}

                <div class="description-section">
                    <p class="description-content">{{ description }}</p>
                </div>

                <div class="metadata-grid">
                    {%- raw -%}
                    {% if version %}
                    <div class="metadata-item">
                        <div class="metadata-label">
                            <i class="fas fa-code-branch"></i>
                            Version
                        </div>
                        <div class="metadata-value">{{ version }}</div>
                    </div>
                    {% endif %}

                    {% if author %}
                    <div class="metadata-item">
                        <div class="metadata-label">
                            <i class="fas fa-user"></i>
                            Author
                        </div>
                        <div class="metadata-value">{{ author }}</div>
                    </div>
                    {% endif %}

                    {% if license %}
                    <div class="metadata-item">
                        <div class="metadata-label">
                            <i class="fas fa-balance-scale"></i>
                            License
                        </div>
                        <div class="metadata-value">{{ license }}</div>
                    </div>
                    {% endif %}

                    {% if requires_python %}
                    <div class="metadata-item">
                        <div class="metadata-label">
                            <i class="fab fa-python"></i>
                            Python Version
                        </div>
                        <div class="metadata-value">{{ requires_python }}</div>
                    </div>
                    {% endif %}

                    {% if keywords %}
                    <div class="metadata-item">
                        <div class="metadata-label">
                            <i class="fas fa-tags"></i>
                            Keywords
                        </div>
                        <div class="tags-container">
                            {% for keyword in keywords %}
                            <span class="tag">{{ keyword }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>

            <div class="command-section">
                <h2 class="command-title">Run this script</h2>
                <div class="command-box">
                    <code>uv run {{ script_source }}</code>
                </div>
                <button class="copy-button" onclick="copyCommand()">
                    <i class="fas fa-copy"></i>
                    Copy Command
                </button>
            </div>

            {% if dependencies %}
            <div class="dependencies-section">
                <h2>Dependencies</h2>
                <ul class="dependencies-list">
                    {% for dependency in dependencies %}
                    <li class="dependency-item">{{ dependency }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            <div class="links-section">
                {% if repository %}
                <a href="{{ repository }}" target="_blank" class="link-item">
                    <i class="fab fa-github"></i>
                    Repository
                </a>
                {% endif %}

                {% if documentation %}
                <a href="{{ documentation }}" target="_blank" class="link-item">
                    <i class="fas fa-book"></i>
                    Documentation
                </a>
                {% endif %}

                {% if homepage %}
                <a href="{{ homepage }}" target="_blank" class="link-item">
                    <i class="fas fa-home"></i>
                    Homepage
                </a>
                {% endif %}

                {% if external_source %}
                <a href="{{ external_source }}" target="_blank" class="link-item">
                    <i class="fas fa-external-link-alt"></i>
                    View Source
                </a>
                {% endif %}
            </div>
            {%- endraw -%}
        </section>
    </main>

    <script>
        function copyCommand() {
            const command = document.querySelector('.command-box code').textContent;
            navigator.clipboard.writeText(command).then(() => {
                const button = document.querySelector('.copy-button');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    button.innerHTML = originalText;
                }, 2000);
            });
        }
    </script>
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

        # Handle script source links
        if "external_source" in metadata:
            # For external scripts, use the original source
            metadata["script_source"] = metadata["external_source"]
        else:
            # For local scripts, use the GitHub Pages URL
            relative_path = os.path.relpath(file_path, BASE_DIR)
            metadata["script_source"] = f"{SITE_CONFIG['base_url']}/{relative_path}"

        # Handle cover image
        if not metadata.get("cover_image"):
            # Check for local cover.png
            cover_path = os.path.join(os.path.dirname(file_path), "cover.png")
            if os.path.exists(cover_path):
                relative_cover = os.path.relpath(cover_path, BASE_DIR)
                metadata["cover_image"] = f"{SITE_CONFIG['base_url']}/{relative_cover}"

    print(f"Metadata extracted from {file_path}: {metadata}")
    return metadata



def copy_files(source_dir, target_dir, extensions=None):
    """Copy files with specific extensions from source to target directory."""
    if extensions is None:
        extensions = []
    os.makedirs(target_dir, exist_ok=True)
    
    # Add debug logging
    print(f"Debug: Copying files from {source_dir} to {target_dir}")
    print(f"Debug: Looking for extensions: {extensions}")
    
    for file_name in os.listdir(source_dir):
        if any(file_name.endswith(ext) for ext in extensions):
            source_path = os.path.join(source_dir, file_name)
            target_path = os.path.join(target_dir, file_name)
            print(f"Debug: Copying {source_path} to {target_path}")
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
            
            tool_definition = f"""\\
@mcp.tool()
def {sanitized_function_name}_run():
    \\"\\"\\"
    Run external script: {solution['name']}
    
    This script is sourced from: {solution['external_source']}
    \\"\\"\\"
    import subprocess
    import threading
    import tempfile
    import urllib.request
    
    def run_command():
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            try:
                urllib.request.urlretrieve('{solution['external_source']}', tmp.name)
                command = "uv run " + tmp.name
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print("Command failed with error: " + result.stderr) 
                else:
                    print("Command output: " + result.stdout.strip())
            finally:
                os.unlink(tmp.name)
    
    thread = threading.Thread(target=run_command, daemon=True)
    thread.start()
    return "Command is running in the background."
"""
            tool_definitions.append(tool_definition)
            continue

        # Use script_source instead of uv_command
        solution_dir = os.path.dirname(solution["script_source"].replace(f"{base_url}/", ""))
        solution_path = os.path.join(BASE_DIR, solution_dir)
        
        if not os.path.exists(solution_path):
            print(f"Directory not found: {solution_path}. Skipping.")
            continue

        python_files = sorted(
            [f for f in os.listdir(solution_path) if f.endswith(".py")],
            reverse=True,
        )
        if not python_files:
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
                args_def = ", ".join(
                    f"{arg['name']}: {arg['type']} = {repr(arg['default'])}" if arg["default"] is not None
                    else f"{arg['name']}: {arg['type']}"
                    for arg in command["arguments"]
                )
                args_cmd = " ".join(
                    f"--{arg['name']} " + arg['name']
                    for arg in command["arguments"]
                )
                
                tool_definition = f"""\\
@mcp.tool()
def {sanitized_function_name}_{command_name}({args_def}):
    \\"\\"\\"
    {script_title}

    {script_description}
    \\"\\"\\"
    import subprocess
    import threading

    def run_command():
        args = " {args_cmd}"
        command = "uv run {solution['script_source']}" + args
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("Command failed with error: " + result.stderr)
        else:
            print("Command output: " + result.stdout.strip())

    thread = threading.Thread(target=run_command, daemon=True)  
    thread.start()
    return "Command is running in the background."
"""
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

def get_cover_image_path(solution_entry, entry, solution_name, metadata, site_config):
    """Helper function to consistently resolve cover image paths."""
    if os.path.exists(os.path.join(solution_entry.path, COVER_IMAGE)):
        return f"{site_config['base_url']}/{entry.name}/{solution_name}/{COVER_IMAGE}"
    elif "cover_image" in metadata:
        return metadata["cover_image"]
    return None

def generate_static_site(base_dir, static_dir):
    """Generate the static site with proper site_config handling."""
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

                    # Copy local files including cover image
                    copy_files(solution_entry.path, solution_output, extensions=[".py", ".png"])

                    # Get cover image path consistently
                    cover_image_path = get_cover_image_path(
                        solution_entry, entry, solution_name, metadata, SITE_CONFIG
                    )
                    
                    base_url = SITE_CONFIG['base_url']
                    script_path = f"{entry.name}/{solution_name}/{most_recent_file}"
                    
                    solution_metadata = {
                        "name": metadata.get("title", solution_name),
                        "description": metadata.get("description", "No description provided."),
                        "link": f"{entry.name}/{solution_name}",
                        "cover": cover_image_path,  # Use consistent cover image path
                        "author": metadata.get("author", ""),
                        "version": metadata.get("version", ""),
                        "external_source": metadata.get("external_source", ""),
                        "script_source": f"{base_url}/{script_path}",
                    }

                    # Generate solution page with consistent cover image path
                    template_vars = {
                        'title': solution_metadata["name"],
                        'project_name': SITE_CONFIG['project_name'],
                        'site_config': SITE_CONFIG,
                        'cover_image': cover_image_path,  # Use same cover image path
                        'description': solution_metadata["description"],
                        'author': metadata.get("author", ""),
                        'version': metadata.get("version", ""),
                        'license': metadata.get("license", ""),
                        'dependencies': metadata.get("dependencies", []),
                        'external_source': solution_metadata["external_source"],
                        'script_source': solution_metadata["script_source"],
                        'keywords': metadata.get("keywords", []),
                        'requires_python': metadata.get("requires_python", ""),
                        'repository': metadata.get("repository", ""),
                        'documentation': metadata.get("documentation", ""),
                        'homepage': metadata.get("homepage", "")
                    }
                    
                    with open(os.path.join(solution_output, "index.html"), "w") as f:
                        f.write(Template(SOLUTION_TEMPLATE).render(**template_vars))
                    solutions.append(solution_metadata)

    # Generate index page and sitemap
    with open(os.path.join(static_dir, "index.html"), "w") as f:
        context = {
            'solutions': solutions,
            'site_config': SITE_CONFIG,
            'categories': list(set(s["link"].split("/")[0] for s in solutions))
        }
        f.write(Template(INDEX_TEMPLATE).render(**context))
    
    generate_sitemap_txt(solutions, static_dir)
    
    # Generate MCP server code
    tool_definitions = generate_mcp_tool_definitions_with_ast(solutions)
    with open(MCP_SERVER_PATH, "w") as f:
        f.write(Template("""
from fastmcp import FastMCP
from typing import Optional, List, Union
import subprocess

mcp = FastMCP("Demo 🚀")

{{ tool_definitions }}

if __name__ == "__main__":
    mcp.run()
""").render(tool_definitions=tool_definitions))
    print(f"mcp_server.py generated at {MCP_SERVER_PATH}")

if __name__ == "__main__":
    generate_static_site(BASE_DIR, STATIC_DIR)
