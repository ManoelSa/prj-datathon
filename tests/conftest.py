import sys
import os
from pathlib import Path

# Adiciona o diretório raiz (projeto) ao sys.path
# Isso permite que os testes importem 'app' e 'src' como pacotes
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
