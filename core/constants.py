import os
from dotenv import load_dotenv

load_dotenv()

class MarketConstants:
    """Regras de negócio e filtros do mercado financeiro brasileiro."""
    
    # Filtros BDI: 02 (Lote Padrão), 03 (Cotas de Fundos)
    ALLOWED_BDI_CODES = os.getenv("ALLOWED_BDI_CODES", "02").split(",")
    
    # Liquidez: Volume financeiro mínimo (100 Milhões padrão)
    DEFAULT_MIN_VOLUME = float(os.getenv("MIN_VOLUME_FILTER", 100000000))

    # Colunas obrigatórias após processamento ETL
    REQUIRED_COLUMNS = [
        "data_pregao", "ticker", "abertura", 
        "maximo", "minimo", "fechamento", "volume"
    ]

class B3Layout:
    """Definições técnicas do arquivo TXT da B3 (COTAHIST)."""
    LAYOUT = {
        "colspecs": [
            (0, 2), (2, 10), (10, 12), (12, 24), (27, 39), 
            (56, 69), (69, 82), (82, 95), (95, 108), (108, 121), 
            (152, 170), (170, 188),
        ],
        "names": [
            "tipo_registro", "data_pregao", "cod_bdi", "ticker", "nome_empresa",
            "abertura", "maximo", "minimo", "medio", "fechamento", 
            "qtd_titulos", "volume"
        ]
    }

class CacheConstants:
    """Nomes de tabelas para persistência no banco."""
    TABLE_HISTORICO = "cotacoes_historicas"
    TABLE_METRICS = "metricas_ativos"

class ChartConfig:
    """Identidade visual dos gráficos (Matplotlib e Front-end)."""
    STYLE = "dark_background"
    FACE_COLOR = "#000000"
    LINE_COLOR = "#facc15"    # Amarelo B3 Terminal
    VOLUME_COLOR = "#3b82f6"  # Azul para Volume
    GRID_COLOR = "#222222"
    
    ALLOWED_TYPES = {
        "fechamento": "Preço de Fechamento",
        "abertura": "Preço de Abertura",
        "volume": "Volume de Negociação"
    }

class ErrorMessages:
    INTERNAL_ERROR = "Erro interno no servidor de dados."
    
    @staticmethod
    def NOT_FOUND(ticker: str) -> str:
        return f"Ativo '{ticker}' não encontrado ou sem liquidez (Vol < 100M)."

    @staticmethod
    def INVALID_TYPE(received: str) -> str:
        return f"Tipo de gráfico '{received}' é inválido. Use: fechamento, abertura ou volume."