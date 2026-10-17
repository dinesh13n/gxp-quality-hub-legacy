"""Read-only preloaded data verification; never seeds, resets, or modifies data."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
r=subprocess.run([sys.executable,str(root/'scripts/offline_inventory.py')],cwd=root)
sys.exit(r.returncode)
