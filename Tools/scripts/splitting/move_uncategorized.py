import os
import shutil

def move_uncategorized():
    """Moves the uncategorized commands to the correct directory."""
    source = "Tools/data/classified_commands/uncategorized_commands.json"
    destination = "CSConfigGenerator/wwwroot/data/commandschema/uncategorized/uncategorized.json"

    # Create the destination directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    shutil.move(source, destination)
    print(f"Moved '{source}' to '{destination}'")

if __name__ == "__main__":
    move_uncategorized()
