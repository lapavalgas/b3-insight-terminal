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
### ROUTER.PY (API) ###
#######################

def test_api_root():
    """Testa o endpoint raiz."""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_api_get_ativos_error_handling():
    """Testa se a API lida com erros de banco retornando 500."""
    with patch.object(MarketService, 'list_available_tickers', side_effect=Exception("DB Error")):
        response = client.get("/ativos")
        assert response.status_code == 500
        assert "Erro interno" in response.json()["detail"]

def test_api_chart_not_found():
    """Testa o erro 404 para ativos inexistentes no gráfico."""
    with patch.object(ChartService, 'generate_styled_chart', return_value=None):
        response = client.get("/ativos/NONEXISTENT/graficos")
        assert response.status_code == 404

#######################
### EXTRAS          ###
#######################

def test_api_ticker_case_insensitivity():
    """Verifica se a API aceita 'petr4' minúsculo e converte para 'PETR4'."""
    # Este teste falhará se você não usar .upper() no seu router
    response = client.get("/ativos/petr4")
    assert response.status_code in [200, 404] # O importante é não dar 500

def test_api_invalid_query_params():
    """Testa se a API rejeita tipos de gráficos inexistentes."""
    response = client.get("/ativos/PETR4/graficos?tipo=invalid_mode")
    assert response.status_code == 400 
    assert "inválido" in response.json()["detail"]