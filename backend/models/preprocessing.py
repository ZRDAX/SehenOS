import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

# Função para preparar os dados
def preprocess_data(packets):
    """
    Preprocessa os dados dos pacotes capturados para análise.
    """
    df = pd.DataFrame(packets)

    # Converter timestamp para datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        raise ValueError("Coluna 'timestamp' está ausente nos dados.")

    # Ordenar por timestamp
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # Criar coluna calculada
    df["bytes_per_second"] = df["bytes"] / (
        df["timestamp"].diff().dt.total_seconds().fillna(1)
    )

    # Seleção de colunas relevantes
    numeric_cols = ["length", "bytes", "src_port", "dst_port", "time_to_live", "is_blacklisted", "bytes_per_second"]
    df = df.fillna(0)  # Tratar valores nulos

    # Escalonar os dados
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_cols])

    return df, scaled_data


def calculate_entropy(payload):
    if not payload:
        return 0
    counts = np.bincount(bytearray.fromhex(payload))
    probs = counts / sum(counts)
    return -np.sum([p * np.log2(p) for p in probs if p > 0])
