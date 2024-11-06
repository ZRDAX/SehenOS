import psutil
import subprocess
import time

def get_cpu_temp():
    # Comando para obter a temperatura da CPU no Linux
    try:
        temp = subprocess.run(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE)
        # A temperatura é retornada em miligrados, por isso a divisão por 1000
        return int(temp.stdout) / 1000
    except Exception as e:
        return f"Erro ao obter temperatura: {e}"

while True:
    # Uso da CPU (percentual)
    cpu_usage = psutil.cpu_percent(interval=1)

    # Temperatura da CPU
    cpu_temp = get_cpu_temp()

    # Memória RAM
    memory_info = psutil.virtual_memory()

    # Exibir as informações
    print(f"Uso de CPU: {cpu_usage}%")
    print(f"Temperatura da CPU: {cpu_temp}°C")
    print(f"Memória Total: {memory_info.total / (1024 ** 3):.2f} GB")
    print(f"Memória Usada: {memory_info.used / (1024 ** 3):.2f} GB")
    
    # Intervalo de tempo entre as verificações (ex: 3 segundos)
    time.sleep(3)
