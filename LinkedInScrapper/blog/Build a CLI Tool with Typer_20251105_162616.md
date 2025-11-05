# Build a CLI Tool with Typer: Your Passport to Productive Command Lines

Ever found yourself repeatedly running the same sequence of commands, or wishing you could automate a complex workflow with a simple script? If you're building tools for yourself, your team, or even the wider world, a well-crafted Command Line Interface (CLI) can be a game-changer for productivity and user experience.

While Python offers several excellent libraries for building CLIs, one has rapidly gained popularity for its elegance, simplicity, and powerful features: **Typer**. Built on top of FastAPI's core and inspired by Click, Typer makes it incredibly intuitive to define commands, arguments, options, and even rich output with just a few lines of code.

In this post, we're going to dive deep into Typer. We'll build a practical CLI tool from scratch, covering the essentials and highlighting best practices along the way. Get ready to transform your scripts into professional, user-friendly command-line applications!

---

## Why Typer? The Modern CLI Choice

Before we jump into code, let's quickly discuss why Typer often stands out:

*   **Python Type Hints:** This is Typer's superpower. It leverages standard Python type hints to automatically validate arguments, generate help messages, and provide excellent editor support. Less boilerplate, more clarity.
*   **Ease of Use:** If you're familiar with Python decorators, Typer will feel incredibly natural. Defining commands and subcommands is straightforward.
*   **Rich Features:** Out of the box, Typer supports:
    *   Automatic help generation
    *   Arguments and options (short/long forms)
    *   Prompting for input
    *   Subcommands for complex tools
    *   Callback functions
    *   Integration with `rich` for beautiful terminal output
*   **FastAPI Pedigree:** Coming from the same creator as FastAPI, Typer shares its philosophy of developer experience and performance.

---

## Our Project: A Simple "Note Taker" CLI

To illustrate Typer's capabilities, let's build a minimalist "Note Taker" CLI. It will allow us to:

1.  Add a new note with a title and content.
2.  List all existing notes.
3.  Delete a specific note by its title.

We'll keep our "database" simple by just storing notes in a JSON file.

### Setup and First Command

First, let's install Typer and create our project structure.

```bash
mkdir note-taker-cli
cd note-taker-cli
python -m venv .venv
source .venv/bin/activate
pip install "typer[rich]" # [rich] installs the rich library for pretty output
```

Now, create a file named `notes.py`:

```python
# notes.py
import typer
from typing import Optional, List
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()
NOTES_FILE = Path("notes.json")

# --- Helper functions for file operations ---
def _load_notes() -> List[dict]:
    if not NOTES_FILE.exists():
        return []
    with open(NOTES_FILE, "r") as f:
        return json.load(f)

def _save_notes(notes: List[dict]):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)

# --- CLI Commands ---

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the note."),
    content: str = typer.Option("", "--content", "-c", help="Content of the note."),
):
    """
    Adds a new note.
    """
    notes = _load_notes()
    if any(note["title"].lower() == title.lower() for note in notes):
        console.print(f"[bold red]Error:[/bold red] A note with title '{title}' already exists.")
        raise typer.Exit(code=1)

    new_note = {"title": title, "content": content}
    notes.append(new_note)
    _save_notes(notes)
    console.print(f"[bold green]Note added:[/bold green] '{title}'")

if __name__ == "__main__":
    app()
```

Let's break down the `add` command:

*   `@app.command()`: This decorator registers the `add` function as a CLI command.
*   `title: str = typer.Argument(...)`: This defines a required positional argument. `...` (Ellipsis) means it's required. Typer automatically infers the type from the hint `str`.
*   `content: str = typer.Option(...)`: This defines an optional argument that can be passed using `--content` or `-c`. If not provided, it defaults to an empty string.

To run this:

```bash
python notes.py add "Meeting Agenda" -c "Discuss Q3 results and next steps."
# Output: Note added: 'Meeting Agenda'

python notes.py add "Shopping List"
# Output: Note added: 'Shopping List'
```

Try running `python notes.py add --help` to see the automatically generated help message!

---

## Listing and Deleting Notes

Now, let's add the functionality to list and delete notes. We'll use `rich` for a nicer output table.

```python
# notes.py (append these commands)

@app.command()
def list():
    """
    Lists all stored notes.
    """
    notes = _load_notes()
    if not notes:
        console.print("No notes found. Add some with `notes.py add`.")
        return

    table = Table(title="Your Notes")
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Content", style="magenta")

    for note in notes:
        table.add_row(note["title"], note["content"])

    console.print(table)

@app.command()
def delete(
    title: str = typer.Argument(..., help="Title of the note to delete.")
):
    """
    Deletes a specific note by its title.
    """
    notes = _load_notes()
    initial_note_count = len(notes)
    
    notes = [note for note in notes if note["title"].lower() != title.lower()]
    
    if len(notes) == initial_note_count:
        console.print(f"[bold yellow]Warning:[/bold yellow] No note found with title '{title}'.")
        raise typer.Exit(code=1) # Indicate an error for scripting

    _save_notes(notes)
    console.print(f"[bold red]Note deleted:[/bold red] '{title}'")

```

Test it out:

```bash
python notes.py list
# (Outputs a nice table of your notes)

python notes.py delete "Meeting Agenda"
# Output: Note deleted: 'Meeting Agenda'

python notes.py delete "Non Existent Note"
# Output: Warning: No note found with title 'Non Existent Note'.
```

### Best Practices and Tips:

*   **Clear Help Messages:** Always provide descriptive `help` strings for arguments and options. Typer uses these to generate the `--help` output.
*   **Error Handling:** Use `typer.Exit(code=1)` to indicate non-successful termination, which is crucial for scripting.
*   **Input Validation:** Implement checks for duplicate entries or invalid inputs early.
*   **Use `rich` for UX:** For anything beyond plain text, `rich` drastically improves the user experience with colors, tables, progress bars, and more.
*   **Modularity:** For larger CLIs, consider splitting commands into separate modules and using Typer's `app.add_typer()` for subcommands.

---

## Conclusion and Next Steps

You've just built a fully functional CLI tool using Typer! We've covered defining commands, using arguments and options, leveraging type hints for validation, and enhancing output with `rich`. This foundational knowledge empowers you to create powerful and user-friendly command-line applications for various tasks.

**Key Takeaways:**

*   Typer simplifies CLI development with Python type hints and intuitive decorators.
*   `typer.Argument` is for positional arguments; `typer.Option` is for optional flags.
*   `rich` is an excellent companion for creating beautiful and informative terminal output.
*   Always consider error handling and clear help messages for a good user experience.

From here, you can expand our `notes` application with features like:

*   Editing existing notes.
*   Searching notes by keywords.
*   Archiving or tagging notes.
*   Exporting notes to different formats.

Typer is a fantastic tool to have in your developer toolkit. Start building your own CLIs and automate your world, one command at a time!