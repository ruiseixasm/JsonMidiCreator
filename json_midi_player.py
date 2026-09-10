import sys
import json
from jsonmidicreator import Deserialize, Play

def main():
    # 1. Get the file path from the command line
    if len(sys.argv) < 2:
        print("Usage: python run_clip.py <file.json>")
        sys.exit(1)

    path = sys.argv[1]

    # 2. Load the JSON
    with open(path, "r") as f:
        data = json.load(f)

    # 3. Create the Composition
    composition = Deserialize(data)

    # 4. Finnaly play the composition
    composition >> Play(verbose=True)

    print(f"Done: {path}")


if __name__ == "__main__":
    main()
