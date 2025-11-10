import os
from pathlib import Path

# --- Configuration ---
# Directories to ignore completely
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "env",
    ".vscode",
}

# Files to ignore
IGNORE_FILES = {
    ".DS_Store",
}
# ---------------------

def display_tree(start_path: Path):
    """
    Prints a directory tree structure.
    """
    print(f"\n--- Directory Tree for: {start_path.resolve()} ---\n")
    
    # Prefix components:
    space =    "    "
    branch =   "|-- "
    tee =      "|   "
    last =     "|__ "

    def _walk_dir(dir_path: Path, prefix: str = ""):
        """Recursive helper function to walk and print the directory."""
        
        # Get contents, filter out ignored ones
        try:
            contents = [
                p for p in dir_path.iterdir()
                if p.name not in IGNORE_DIRS and p.name not in IGNORE_FILES
            ]
            contents.sort(key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            print(f"{prefix}{branch} [Error: Permission Denied]")
            return

        # Use an iterator to peek at the next item
        pointers = [tee] * (len(contents) - 1) + [last]
        
        for pointer, path in zip(pointers, contents):
            # Print file/folder name
            print(f"{prefix}{pointer}{path.name}")
            
            # If it's a directory, recurse
            if path.is_dir():
                # Determine the prefix for the next level
                # If this is the last item, the prefix is just space
                # Otherwise, it's a tee
                extension = space if pointer == last else tee
                _walk_dir(path, prefix + extension)

    # --- Start the walk ---
    print(f"{start_path.name}/")
    _walk_dir(start_path)
    print("\n--- End of Tree ---")

if __name__ == "__main__":
    # Get the directory where this script is located
    current_dir = Path(os.path.dirname(__file__))
    display_tree(current_dir)