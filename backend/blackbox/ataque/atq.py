import requests
import threading

def send_request():
    try:
        response = requests.get("http://192.168.1.115:5000/api/packets")
        print(f"Resposta: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

threads = []
for i in range(100):  # Cria 100 threads
    thread = threading.Thread(target=send_request)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()