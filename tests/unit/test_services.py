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

#########################
### MARKET_SERVICE.PY ###
#########################

@patch('core.database.db_manager.get_from_cache')
def test_market_service_list_tickers(mock_get):
    """Verifica se a listagem de ativos aplica os filtros corretamente."""
    # Mock de retorno do banco
    mock_get.return_value = pd.DataFrame({"ticker": ["PETR4", "VALE3"]})
    
    service = MarketService()
    tickers = service.list_available_tickers(content_limit=10)
    
    assert len(tickers) == 2
    assert "PETR4" in tickers
    # Verifica se a query SQL gerada contém os códigos BDI permitidos
    args, kwargs = mock_get.call_args
    assert "'02', '03'" in args[0] 

########################
### CHART_SERVICE.PY ###
########################

def test_chart_generation_flow():
    """Testa se o gerador de gráficos retorna um objeto Figure e fecha o buffer."""
    service = ChartService()
    
    # Mock do dado para não precisar de banco real
    with patch.object(MarketService, 'get_ticker_data') as mock_data:
        mock_data.return_value = pd.DataFrame({
            "data_pregao": ["2023-01-01", "2023-01-02"],
            "fechamento": [10.0, 11.0]
        })
        
        fig = service.generate_styled_chart("PETR4", "fechamento")
        assert fig is not None
        
        response = service.create_streaming_response(fig)
        assert response.media_type == "image/png"

#######################
### EXTRAS          ###
#######################

@patch('core.database.db_manager.get_from_cache')
def test_market_service_empty_data(mock_get):
    """Verifica se o serviço lida corretamente com retorno vazio do banco."""
    mock_get.return_value = pd.DataFrame() # Simula ativo que existe mas não tem dados
    
    from services.market_service import MarketService
    service = MarketService()
    data = service.get_ticker_data("NULL3")
    
    assert data.empty
    assert len(data.columns) == 0

def test_chart_service_invalid_figure_handling():
    """Testa se o serviço de gráfico falha graciosamente com dados nulos."""
    from services.chart_service import ChartService
    service = ChartService()
    
    # Tenta gerar gráfico para algo que retorna None
    with patch.object(MarketService, 'get_ticker_data', return_value=pd.DataFrame()):
        fig = service.generate_styled_chart("ERRO4")
        assert fig is None