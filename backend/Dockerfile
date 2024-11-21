# Dockerfile para o backend do SehenOS
FROM python:3.11-slim

# Atualizar e instalar dependências necessárias
RUN apt-get update && apt-get install -y \
        pkg-config \
        libhdf5-dev \
        libpq-dev \
        python3-dev \
        build-essential \
        postgresql-client \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir keras tensorflow

# Copiar o restante do código
COPY . .

# Configurar variáveis de ambiente para o Flask
ENV FLASK_APP=server/routes.py
ENV FLASK_ENV=production

# Expor a porta que o Flask usa
EXPOSE 5000

# Configurar ponto de entrada para iniciar o servidor
CMD ["python3", "server/routes.py"]
