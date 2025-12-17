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
### CONFIG.PY & .ENV ###
#######################

def test_config_directories_creation():
    """Verifica se o sistema cria as pastas base corretamente."""
    settings.setup_directories()
    assert settings.STATIC_DIR.exists()
    if "sqlite" in settings.DB_URL:
        assert (settings.BASE_DIR / "database").exists()

def test_env_loading():
    """Verifica se as variáveis críticas do .env foram carregadas."""
    assert settings.B3_DATA_FILE is not None
    assert isinstance(settings.PORT, int)

#######################
### LAYOUTS & MAIN  ###
#######################

def test_b3_layout_consistency():
    """Valida se o layout B3 tem nomes e colspecs correspondentes."""
    # Importa a classe do novo local
    from core.constants import B3Layout
    
    layout = B3Layout.LAYOUT
    assert len(layout["colspecs"]) == len(layout["names"])

def test_error_messages_formatting():
    """Valida as funções geradoras de mensagens de erro."""
    msg = ErrorMessages.INVALID_TYPE("invalid_type")
    assert "fechamento" in msg
    assert "abertura" in msg

#######################
### EXTRAS          ###
#######################

def test_b3_layout_invalid_data():
    """Valida se o sistema se comporta bem com dados fora do esperado."""
    from core.constants import B3Layout
    # Verifica se as posições do layout não se sobrepõem
    colspecs = B3Layout.LAYOUT["colspecs"]
    for i in range(len(colspecs) - 1):
        assert colspecs[i][1] <= colspecs[i+1][0], f"Sobreposição no campo {i}"

def test_chart_config_allowed_types():
    """Garante que apenas tipos suportados estão na configuração."""
    from core.constants import ChartConfig
    assert "fechamento" in ChartConfig.ALLOWED_TYPES
    assert "volume" in ChartConfig.ALLOWED_TYPES
    # Teste de robustez: um tipo aleatório não deve estar lá
    assert "cripto_meme" not in ChartConfig.ALLOWED_TYPES

def test_required_columns_integrity():
    """Garante que o Layout da B3 provê todas as colunas que o sistema exige."""
    from core.constants import B3Layout, MarketConstants
    
    # O que o sistema pede vs O que o arquivo bruto entrega
    colunas_fornecidas = B3Layout.LAYOUT["names"]
    colunas_exigidas = MarketConstants.REQUIRED_COLUMNS
    
    for col in colunas_exigidas:
        assert col in colunas_fornecidas, f"A coluna obrigatória '{col}' não está no layout da B3!"