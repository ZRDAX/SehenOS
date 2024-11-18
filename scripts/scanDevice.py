import nmap

# Inicializar o scanner
nm = nmap.PortScanner()

# Definir o intervalo de IPs da rede para escanear
network_range = '192.168.1.0/24'

# Fazer a varredura com OS Fingerprinting (-O) e captura de MAC
nm.scan(hosts=network_range, arguments='-O')

# Iterar pelos hosts descobertos
for host in nm.all_hosts():
    print(f"Host: {host} ({nm[host].hostname()})")
    print(f"Status: {nm[host].state()}")

    # Mostrar endereços MAC (se disponíveis)
    if 'mac' in nm[host]['addresses']:
        print(f"MAC Address: {nm[host]['addresses']['mac']}")

    # Mostrar portas abertas
    if 'tcp' in nm[host]:
        for port in nm[host]['tcp']:
            print(f"Porta: {port}\tEstado: {nm[host]['tcp'][port]['state']}\tServiço: {nm[host]['tcp'][port]['name']}")

    # Detectar sistema operacional (OS Fingerprinting)
    if 'osclass' in nm[host]:
        for osclass in nm[host]['osclass']:
            print(f"Sistema Operacional Detectado: {osclass['osfamily']} {osclass['osgen']}")

    print("\n")
