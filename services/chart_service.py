import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from core.constants import ChartConfig
from services.market_service import MarketService
from core.config import settings

class ChartService:
    def __init__(self):
        self.market_service = MarketService()

    def generate_styled_chart(self, ticker: str, chart_type: str = "fechamento"):
        df = self.market_service.get_ticker_data(ticker)
        if df.empty or chart_type not in df.columns: return None

        plt.style.use(ChartConfig.STYLE)
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=ChartConfig.FACE_COLOR)
        
        label = ChartConfig.ALLOWED_TYPES.get(chart_type, "Preço")
        
        if chart_type == "volume":
            # Gráfico de barras para volume
            ax.bar(df['data_pregao'], df[chart_type], color='#3b82f6', alpha=0.7)
        else:
            # Gráfico de linha para preços (fechamento/abertura)
            ax.plot(df['data_pregao'], df[chart_type], color=ChartConfig.LINE_COLOR, linewidth=1.5)

        ax.set_title(f"{ticker} - {label}", color="white", fontsize=14, pad=20)
        
        ax.set_facecolor(ChartConfig.FACE_COLOR)
        ax.grid(True, color=ChartConfig.GRID_COLOR, linestyle='--', alpha=0.3)
        
        return fig

    def create_streaming_response(self, fig, download=False, ticker="", chart_type=""):
        """Transforma a figura em um fluxo de dados para o FastAPI."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig) # Importante: Libera memória

        headers = {}
        if download:
            filename = f"chart_{ticker}_{chart_type}.png"
            headers["Content-Disposition"] = f"attachment; filename={filename}"

        return StreamingResponse(buf, media_type="image/png", headers=headers)