# services/market_service.py
import pandas as pd
from core.database import db_manager
from core.constants import MarketConstants, CacheConstants
from core.config import settings

class MarketService:
    def list_available_tickers(self, content_limit: int = 500):
        """Lista tickers que possuem volume financeiro relevante."""
        
        # Como MarketConstants.ALLOWED_BDI_CODES é ('02', '03')
        # transformamos em uma string pronta para o SQL: "'02', '03'"
        bdi_string = ", ".join([f"'{b}'" for b in MarketConstants.ALLOWED_BDI_CODES])
        
        query = f"""
            SELECT DISTINCT ticker FROM {CacheConstants.TABLE_HISTORICO}
            WHERE volume >= :min_vol
            AND cod_bdi IN ({bdi_string})
            LIMIT :limit
        """
        
        params = {
            "min_vol": MarketConstants.DEFAULT_MIN_VOLUME,
            "limit": content_limit
        }
        
        # O SQLite não verá um "?" no lugar da lista, mas sim os valores reais
        df = db_manager.get_from_cache(query, params)
        return df['ticker'].tolist() if not df.empty else []

    def get_ticker_data(self, ticker: str):
        """Busca o histórico completo de um ativo específico."""
        query = f"SELECT * FROM {CacheConstants.TABLE_HISTORICO} WHERE ticker = :t ORDER BY data_pregao ASC"
        return db_manager.get_from_cache(query, {"t": ticker.upper()})