import shutil
import os
from pathlib import Path

def clean():
    folders_to_remove = ['__pycache__', '.pytest_cache', '.ipynb_checkpoints']
    files_to_remove = ['*.pyc', '*.pyo', 'b3_cotacoes.db'] # Nome do seu DB

    print("Iniciando limpeza do projeto...")
    
    for path in Path(".").rglob("*"):
        if path.is_dir() and path.name in folders_to_remove:
            print(f"Removendo pasta: {path}")
            shutil.rmtree(path)
        elif path.is_file() and any(path.match(pattern) for pattern in files_to_remove):
            print(f"Removendo arquivo: {path}")
            os.remove(path)

    print("Projeto limpo com sucesso!")

if __name__ == "__main__":
    clean()