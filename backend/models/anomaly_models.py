import pickle
import os
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.datasets import make_blobs
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.utils import register_keras_serializable, get_custom_objects
from tensorflow.keras.losses import MeanSquaredError
from tensorflow import reduce_mean
import numpy as np  # Corrigido aqui

# Garantir que o diretório existe
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Treinar Isolation Forest
def train_isolation_forest(data, contamination=0.05):
    model_dir = "/home/zrdax/SehenOS/backend/models/pipes/"
    ensure_directory_exists(model_dir)
    model_path = os.path.join(model_dir, "isolation_forest.pkl")

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(data)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Modelo Isolation Forest salvo em: {model_path}")
    return model

# Treinar Autoencoder
def train_autoencoder(data, input_dim):
    model_dir = "/home/zrdax/SehenOS/backend/models/pipes/"
    ensure_directory_exists(model_dir)
    model_path = os.path.join(model_dir, "autoencoder.keras")

    autoencoder = Sequential([
        Input(shape=(input_dim,)),
        Dense(16, activation='relu'),
        Dense(8, activation='relu'),
        Dense(16, activation='relu'),
        Dense(input_dim, activation='linear')
    ])
    autoencoder.compile(optimizer='adam', loss=MeanSquaredError())
    autoencoder.fit(data, data, epochs=50, batch_size=32, verbose=1)
    save_model(autoencoder, model_path)  # Corrigido aqui
    print(f"Modelo Autoencoder salvo em: {model_path}")
    return autoencoder

# Treinar PCA
def train_pca(data, n_components=2):
    model_dir = "/home/zrdax/SehenOS/backend/models/pipes/"
    ensure_directory_exists(model_dir)
    model_path = os.path.join(model_dir, "pca.pkl")

    pca = PCA(n_components=n_components)
    pca.fit(data)
    with open(model_path, "wb") as f:
        pickle.dump(pca, f)
    print(f"Modelo PCA salvo em: {model_path}")
    return pca

# Carregar Modelos
def load_models():
    model_dir = "/home/zrdax/SehenOS/backend/models/pipes/"
    try:
        with open(os.path.join(model_dir, "isolation_forest.pkl"), "rb") as f:
            isolation_forest = pickle.load(f)
        autoencoder = load_model(os.path.join(model_dir, "autoencoder.keras"))
        with open(os.path.join(model_dir, "pca.pkl"), "rb") as f:
            pca = pickle.load(f)
        print("Modelos carregados com sucesso.")
        return isolation_forest, autoencoder, pca
    except Exception as e:
        print(f"Erro ao carregar modelos: {e}")
        return None, None, None

# Gerar e treinar os modelos
if __name__ == "__main__":
    print("Gerando dados fictícios...")
    X = np.random.rand(1000, 7)  # Simulando dados com 7 features

    print("Treinando e salvando os modelos...")
    train_isolation_forest(X)
    train_autoencoder(X, input_dim=X.shape[1])
    train_pca(X)
