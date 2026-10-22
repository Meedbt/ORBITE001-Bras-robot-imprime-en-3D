import sys,runpy
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,'C:/Users/mouha/Documents/Codex/2026-10-21/salut-alors-la-j-ai-envie-3/work/cad-deps')
target=sys.argv.pop(1)
runpy.run_path(str(Path(__file__).parent/target),run_name='__main__')
