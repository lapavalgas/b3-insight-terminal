import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Config:
    """Configurações de infraestrutura e ambiente (Infra Only)."""
    
    # --- DIRETÓRIOS ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # --- BANCO DE DADOS ---
    DB_URL = os.getenv("DB_CONNECTION_STRING", "sqlite:///database/b3_cotacoes.db")
    
    # --- ARQUIVOS E PASTAS ---
    # Define onde os gráficos serão salvos fisicamente (caso use Matplotlib no servidor)
    STATIC_DIR = BASE_DIR / os.getenv("STATIC_PATH", "static/charts")
    B3_DATA_FILE = os.getenv("B3_FILE_PATH")
    
    # --- API ---
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"

    @classmethod
    def setup_directories(cls):
        """Cria as pastas necessárias ao iniciar o app."""
        cls.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        # Se for SQLite, garante que a pasta do banco existe
        if "sqlite" in cls.DB_URL:
            db_path = Path(cls.DB_URL.replace("sqlite:///", "")).parent
            db_path.mkdir(parents=True, exist_ok=True)

# Instância global
settings = Config()