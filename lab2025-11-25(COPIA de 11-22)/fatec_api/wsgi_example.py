# wsgi_example.py — exemplo de configuração WSGI para PythonAnywhere
import sys
from pathlib import Path
project_home = str(Path('/home/<seu-usuario>').resolve())
if project_home not in sys.path:
    sys.path.insert(0, project_home)
from app import app as application
