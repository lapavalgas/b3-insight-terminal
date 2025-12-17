import pytest
import pandas as pd
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Importações do projeto
from core.config import settings
from core.constants import MarketConstants, ErrorMessages
from core.database import db_manager
from services.market_service import MarketService
from services.chart_service import ChartService
from api.router import app 

client = TestClient(app)

#######################
### DATABASE.PY     ###
#######################

def test_database_connection():
    """Testa se a conexão com o banco está operacional."""
    session = db_manager.get_session()
    assert session is not None
    session.close()

def test_save_and_get_cache():
    """Testa o ciclo de vida de dados no cache (salvamento e leitura)."""
    test_df = pd.DataFrame([{"ticker": "TEST3", "fechamento": 10.5, "volume": 500000}])
    table_name = "test_table"
    
    # Salva
    success = db_manager.save_to_cache(test_df, table_name, if_exists='replace')
    assert success is True
    
    # Recupera
    query = f"SELECT * FROM {table_name} WHERE ticker = :t"
    recovered_df = db_manager.get_from_cache(query, {"t": "TEST3"})
    
    assert not recovered_df.empty
    assert recovered_df.iloc[0]['ticker'] == "TEST3"
