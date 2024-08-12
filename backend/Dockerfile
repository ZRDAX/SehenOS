FROM python:3.9

# Instalar libhdf5-dev *problemas com TensorFlow*
RUN apt-get update && apt-get install -y libhdf5-dev

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "app.py"]

