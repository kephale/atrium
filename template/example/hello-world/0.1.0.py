[% if include_example_script %]
================
File: template/example/hello-world/0.1.0.py
================
# /// script
# title = "Hello World"
# description = "A simple example script that prints a greeting"
# author = "{{ author_name }} <{{ author_email }}>"
# license = "MIT"
# version = "0.1.0"
# keywords = ["example", "hello-world"]
# repository = "https://github.com/{{ github_username }}/{{ project_name }}"
# documentation = "https://github.com/{{ github_username }}/{{ project_name }}#readme"
# homepage = "https://{{ github_username }}.github.io/{{ project_name }}"
# requires-python = ">={{ minimum_python_version }}"
# dependencies = [
# "typer"
# ]
# ///

import typer
from typing import Optional

app = typer.Typer(help="A simple hello world script")

@app.command()
def greet(
    name: Optional[str] = typer.Option(None, help="Name to greet")
):
    """
    Print a greeting message
    """
    if name:
        typer.echo(f"Hello, {name}!")
    else:
        typer.echo("Hello, World!")

if __name__ == "__main__":
    app()
[% endif %]