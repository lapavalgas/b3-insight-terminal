import sys
import os
from pathlib import Path

# Adiciona a pasta raiz ao sys.path para que 'services' e 'core' sejam encontrados
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

from services.market_service import MarketService
from services.analysis_service import AnalysisService
from services.chart_service import ChartService
from core.constants import ChartConfig, ErrorMessages
from core.config import settings as config

router = APIRouter()

#---------------------
# --- DEPENDÊNCIAS ---
#---------------------

def get_market_service():
    return MarketService()

def get_analysis_service():
    return AnalysisService()

def get_chart_service():
    return ChartService()

#---------------------
# --- ENDPOINTS    ---
#---------------------

# Health Check

@router.get("/", tags=["Raiz"])
def raiz():
    return {"message": "Bem-vindo à API de Cotações B3!", "version": "3.1.0"}

# Ativos Disponíveis

@router.get("/ativos", summary="Listar Ativos Disponíveis", tags=["Ativos"])
def listar_ativos(
    limit: int = Query(500, description="Limite de ativos"), 
    service: MarketService = Depends(get_market_service)
):
    try:
        # IMPORTANTE: No MarketService, o método deve aceitar content_limit
        # E certifique-se de que a função no service tem o (self, content_limit)
        ativos = service.list_available_tickers(content_limit=limit)
        return {"total": len(ativos), "ativos": ativos}
    except Exception as e:
        print(f"Erro no endpoint /ativos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Dados Históricos do Ativo

@router.get("/ativos/{ativo}", summary="Dados Históricos", tags=["Ativos"])
def obter_historico_ativo(ativo: str, service: MarketService = Depends(get_market_service)):
    df = service.get_ticker_data(ativo.upper())
    if df.empty:
        raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND(ativo))
    return df.to_dict(orient="records")

# Gráfico do Ativo

@router.get("/ativos/{ativo}/graficos", tags=["Visualização"])
def obter_grafico_imagem(
    ativo: str, 
    tipo: str = "fechamento",
    service: ChartService = Depends(get_chart_service)
):
    
    tipo = tipo.lower()
    if tipo not in ChartConfig.ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=ErrorMessages.INVALID_TYPE(tipo)
        )
    
    fig = service.generate_styled_chart(ativo.upper(), tipo.lower())
    if fig is None:
        raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND(ativo))
    return service.create_streaming_response(fig)

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return None

#-----------------------------
# --- INICIALIZAÇÃO DA APP ---
#-----------------------------

app = FastAPI(title="B3 API Otimizada")

# Adicione o CORS caso vá usar com o index.html
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)