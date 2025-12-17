from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import pandas as pd
import logging
from .config import settings
from .constants import CacheConstants

# Configuração de Logging para monitorar operações de banco
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerencia a conexão com o banco de dados e operações de persistência (Cache).
    """
    def __init__(self):
        self.engine = create_engine(
            settings.DB_URL, 
            connect_args={"check_same_thread": False} if "sqlite" in settings.DB_URL else {}
        )
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_session(self):
        """Retorna uma nova sessão de banco de dados."""
        return self.Session()

    def save_to_cache(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace'):
        """
        Salva um DataFrame no banco de dados como cache.
        """
        try:
            if df is None or df.empty:
                return False
            
            df.to_sql(
                name=table_name, 
                con=self.engine, 
                if_exists=if_exists, 
                index=True
            )
            logger.info(f"Cache atualizado na tabela: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar cache em {table_name}: {e}")
            return False

    def get_from_cache(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Executa uma consulta e retorna um DataFrame.
        """
        try:
            return pd.read_sql(text(query), self.engine, params=params)
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return pd.DataFrame()

    def execute_raw(self, sql: str, params: dict = None):
        """Executa um comando SQL puro (INSERT/UPDATE/DELETE)."""
        with self.engine.begin() as conn:
            conn.execute(text(sql), params or {})

# Instância única para o projeto todo
db_manager = DatabaseManager()