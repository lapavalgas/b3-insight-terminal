from core.database import db_manager
from core.config import settings
import pandas as pd
from core.constants import B3Layout 

class B3ETLProcessor:
    def import_raw_file(self, file_path):
        print(f"Lendo arquivo: {file_path}")
        # Usa o B3_LAYOUT para processar o TXT
        B3_LAYOUT = B3Layout.LAYOUT
        df = pd.read_fwf(
            file_path, 
            colspecs=B3_LAYOUT["colspecs"], 
            names=B3_LAYOUT["names"],
            skiprows=1, skipfooter=1
        )

        # Converte o formato 20250102 (string/int) para data real
        df['data_pregao'] = pd.to_datetime(df['data_pregao'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

        # Converter colunas numéricas (abertura, fechamento) que vêm com vírgula implícita
        # A B3 envia 0000000001050 para significar 10.50
        cols_precos = ['abertura', 'maximo', 'minimo', 'fechamento']
        for col in cols_precos:
            df[col] = df[col] / 100.0

        # Lógica de limpeza...
        db_manager.save_to_cache(df, "cotacoes_historicas")
        print("Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    processor = B3ETLProcessor()
    processor.import_raw_file(settings.B3_DATA_FILE)