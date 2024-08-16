FROM python:3.11-slim

# Instalar libhdf5-dev por conta da biblioteca dar erro na hora de instalar hdf5 no TensorFlow
# Instalar as dependencias nescessarias para instalar o psycopg2
RUN apt-get update && apt-get install -y \
        pkg-config \
        libhdf5-dev \
        libpq-dev \
        python3-dev \
        build-essential \
        postgresql-client \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install h5py TensorFlow

COPY . .

# Expor a porta que o Flask usa
EXPOSE 5000

ENTRYPOINT ["./wait_for_db.sh", "python3", "app.py"]

