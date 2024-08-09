import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# Carregar os dados pré-processados
df_preprocessed = pd.read_csv('tables/preprocessed_data.csv')

# Preparar os dados para TensorFlow
features = df_preprocessed.drop(columns=['Intrusion']).values
labels = (df_preprocessed['Intrusion'] != 'unknown').astype(int).values

# Criar o modelo
model = Sequential([
    Dense(64, activation='relu', input_shape=(features.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

# Compilar o modelo
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Treinar o modelo
model.fit(features, labels, epochs=20, batch_size=32, shuffle=True)

# Avaliar o modelo
loss, accuracy = model.evaluate(features, labels)
print(f'Accuracy: {accuracy:.4f}')

# Converter para TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Salvar o modelo convertido
with open('models/anomaly_detection_model.tflite', 'wb') as f:
    f.write(tflite_model)
