FROM python:3.11-slim

# Instalar libhdf5-dev por conta da biblioteca dar erro na hora de instalar hdf5 no TensorFlow
# Instalar as dependencias nescessarias para instalar o psycopg2
RUN apt-get update && apt-get install -y \
        libhdf5-dev \
        libpq-dev \
        python3-dev \
        build-essential \
        --no-install-recommends && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install --update pip
RUN pip install h5py TensorFlow

COPY . .

# Expor a porta que o Flask usa
EXPOSE 5000

CMD ["python3", "app.py"]
#CMD ["python3", "packet_capture.py"]

