import psutil
import subprocess

def get_system_info():
    """
    Retorna informações sobre o sistema.
    """
    info = {
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().used / 1e9:.2f}GB / {psutil.virtual_memory().total / 1e9:.2f}GB",
        "disk_usage": f"{psutil.disk_usage('/').used / 1e9:.2f}GB / {psutil.disk_usage('/').total / 1e9:.2f}GB",
        "temperature": get_temperature(),
    }
    return info

def get_temperature():
    """
    Obtém a temperatura do sistema. Funciona apenas em sistemas compatíveis.
    """
    try:
        # Método para sistemas Linux
        result = subprocess.run(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE)
        temp_output = result.stdout.decode()
        return temp_output.split("=")[1].strip() if "temp" in temp_output else "N/A"
    except Exception:
        return "N/A"
