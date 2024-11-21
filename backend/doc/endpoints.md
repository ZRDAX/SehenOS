# Comandos CURL para Interação com o Servidor para o Exemplo de Test

## Obter Pacotes
```bash
curl http://localhost:5000/packets

curl http://localhost:5000/anomalies

curl -X POST -H "Content-Type: application/json" \
    -d '{"action": "add", "ip": "192.168.0.100"}' \
    http://localhost:5000/blacklist_edit

curl -X POST http://localhost:5000/reboot_sys

curl -X POST http://localhost:5000/reboot_sys

