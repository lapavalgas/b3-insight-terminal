# services/analysis_service.py
import pandas as pd
from core.database import db_manager
from core.constants import CacheConstants
from core.config import settings

class AnalysisService:
    def get_metrics(self, ticker: str):
        """Retorna métricas calculadas, buscando no cache ou calculando na hora."""
        ticker = ticker.upper()
        # 1. Tenta buscar no cache
        query_cache = f"SELECT * FROM {CacheConstants.TABLE_METRICS} WHERE ticker = :t"
        cache = db_manager.get_from_cache(query_cache, {"t": ticker})
        
        if not cache.empty:
            return cache.to_dict(orient="records")[0]

        # 2. Se não houver cache, calcula (Exemplo simplificado)
        from services.market_service import MarketService
        df = MarketService().get_ticker_data(ticker)
        
        if df.empty: return None

        metrics = {
            "ticker": ticker,
            "media_fechamento": float(df['fechamento'].mean()),
            "maxima_periodo": float(df['maximo'].max()),
            "volatilidade": float(df['fechamento'].std())
        }
        
        # 3. Salva o novo cálculo no cache
        db_manager.save_to_cache(pd.DataFrame([metrics]), CacheConstants.TABLE_METRICS, if_exists='append')
        
        return metrics