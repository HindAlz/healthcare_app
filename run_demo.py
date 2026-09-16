"""Launch Streamlit using the isolated synthetic data directory."""
import os
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    root=Path(__file__).resolve().parent
    env=os.environ.copy()
    env['HEALTHCARE_DATA_DIR']=str(root/'data'/'demo')
    raise SystemExit(subprocess.call([sys.executable,'-m','streamlit','run','app.py'],cwd=root,env=env))
