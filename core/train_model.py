import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
import torch.optim as optim

# Carregar os dados pré-processados
df_preprocessed = pd.read_csv('preprocessed_data.csv')

# Preparar os dados para PyTorch
features = df_preprocessed.drop(columns=['Intrusion']).values
labels = (df_preprocessed['Intrusion'] != 'unknown').astype(int).values

features_tensor = torch.tensor(features, dtype=torch.float32)
labels_tensor = torch.tensor(labels, dtype=torch.float32)

dataset = TensorDataset(features_tensor, labels_tensor)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

class AnomalyDetectionModel(nn.Module):
    def __init__(self, input_dim):
        super(AnomalyDetectionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

# Definir o modelo, critério de perda e otimizador
input_dim = features.shape[1]
model = AnomalyDetectionModel(input_dim)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Treinar o modelo
num_epochs = 20
for epoch in range(num_epochs):
    model.train()
    epoch_loss = 0
    for inputs, targets in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs).squeeze()
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    
    print(f'Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss/len(train_loader)}')

# Avaliar o modelo
model.eval()
with torch.no_grad():
    test_outputs = model(features_tensor).squeeze()
    test_preds = (test_outputs > 0.5).int()
    accuracy = (test_preds == labels_tensor).float().mean()
    print(f'Accuracy: {accuracy:.4f}')

# Salvar o modelo treinado
torch.save(model.state_dict(), 'anomaly_detection_model.pth')
