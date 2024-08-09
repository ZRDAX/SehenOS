import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models

# Carregar os dados pré-processados
df_preprocessed = pd.read_csv('tables/preprocessed_data.csv')

# Preparar os dados para TensorFlow
features = df_preprocessed.drop(columns=['Intrusion']).values
labels = (df_preprocessed['Intrusion'] != 'unknown').astype(int).values

# Definir o modelo
model = models.Sequential([
    layers.Dense(64, activation='relu', input_shape=(features.shape[1],)),
    layers.Dense(32, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

# Compilar o modelo
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Treinar o modelo
model.fit(features, labels, epochs=20, batch_size=32)

# Avaliar o modelo
accuracy = model.evaluate(features, labels)[1]
print(f'Accuracy: {accuracy:.4f}')

# Converter para TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Salvar o modelo TFLite
with open('models/anomaly_detection_model.tflite', 'wb') as f:
    f.write(tflite_model)
