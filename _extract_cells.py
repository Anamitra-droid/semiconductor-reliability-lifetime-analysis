import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb["cells"]):
    print(f"=== CELL {i} ({cell['cell_type']}) ===")
    print("".join(cell.get("source", [])))
    print()
