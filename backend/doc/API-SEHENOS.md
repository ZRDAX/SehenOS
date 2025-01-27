
# Documentação da API do Backend

## **Base URL**
A API está disponível no endereço:

```
http://<API_HOST>:<PORT>
```

Substitua `<API_HOST>` pelo IP ou domínio do servidor e `<PORT>` pela porta configurada (ex.: `5000` para desenvolvimento).

---

## **Endpoints Disponíveis**

### **1. Gerenciamento de Pacotes**

#### **Listar Pacotes Capturados**
- **URL:** `/packets`
- **Método:** `GET`
- **Descrição:** Retorna todos os pacotes capturados no Redis.

**Exemplo de Requisição:**
```bash
curl http://localhost:5000/packets
```

**Resposta de Sucesso (JSON):**
```json
[
    {
        "timestamp": "2024-11-19T12:34:56.789",
        "src_ip": "192.168.0.1",
        "dst_ip": "8.8.8.8",
        "protocol": 6,
        "length": 128,
        "mac_src": "00:11:22:33:44:55",
        "mac_dst": "66:77:88:99:AA:BB",
        "src_port": 12345,
        "dst_port": 53,
        "tcp_flags": "S",
        "payload": "48656c6c6f20776f726c64",
        "blacklist_flag": false,
        "whitelist_flag": true,
        "bytes": 128
    }
]
```

---

### **2. Gerenciamento de Anomalias**

#### **Listar Anomalias Detectadas**
- **URL:** `/anomalies`
- **Método:** `GET`
- **Descrição:** Retorna todas as anomalias detectadas.

**Exemplo de Requisição:**
```bash
curl http://localhost:5000/anomalies
```

**Resposta de Sucesso (JSON):**
```json
[
    {
        "timestamp": "2024-11-19T12:35:20.123",
        "src_ip": "192.168.0.2",
        "dst_ip": "8.8.4.4",
        "protocol": 17,
        "length": 512,
        "isolation_anomaly": true,
        "reconstruction_error": 0.02
    }
]
```

---

### **3. Backups**

#### **Listar Backups de Pacotes**
- **URL:** `/list_packet_backup`
- **Método:** `GET`
- **Descrição:** Retorna a lista de arquivos de backup de pacotes.

**Exemplo de Requisição:**
```bash
curl http://localhost:5000/list_packet_backup
```

**Resposta de Sucesso (JSON):**
```json
{
    "backups": [
        "packets_20241119_123456.json",
        "packets_20241120_101010.json"
    ]
}
```

#### **Salvar Backup Manualmente de Pacotes**
- **URL:** `/save_packet_backup`
- **Método:** `POST`
- **Descrição:** Salva manualmente um backup dos pacotes capturados.

**Exemplo de Requisição:**
```bash
curl -X POST http://localhost:5000/save_packet_backup
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "backup_file": "backup/packets_20241120_103012.json"
}
```

#### **Listar Backups de Anomalias**
- **URL:** `/list_anomaly_backup`
- **Método:** `GET`
- **Descrição:** Retorna a lista de arquivos de backup de anomalias.

**Exemplo de Requisição:**
```bash
curl http://localhost:5000/list_anomaly_backup
```

**Resposta de Sucesso (JSON):**
```json
{
    "backups": [
        "anomalies_20241119_123456.json",
        "anomalies_20241120_101010.json"
    ]
}
```

#### **Salvar Backup Manualmente de Anomalias**
- **URL:** `/save_anomaly_backup`
- **Método:** `POST`
- **Descrição:** Salva manualmente um backup das anomalias detectadas.

**Exemplo de Requisição:**
```bash
curl -X POST http://localhost:5000/save_anomaly_backup
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "backup_file": "backup/anomalies_20241120_103012.json"
}
```

---

### **4. Sistema**

#### **Obter Informações do Sistema**
- **URL:** `/system_info`
- **Método:** `GET`
- **Descrição:** Retorna informações do sistema, como CPU, RAM e temperatura.

**Exemplo de Requisição:**
```bash
curl http://localhost:5000/system_info
```

**Resposta de Sucesso (JSON):**
```json
{
    "cpu_usage": "12%",
    "memory_usage": "1.5GB / 4GB",
    "disk_usage": "8GB / 32GB",
    "temperature": "45°C"
}
```

#### **Desligar o Sistema**
- **URL:** `/shutdown_sys`
- **Método:** `POST`
- **Descrição:** Envia um comando para desligar o sistema.

**Exemplo de Requisição:**
```bash
curl -X POST http://localhost:5000/shutdown_sys
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "message": "Sistema será desligado."
}
```

#### **Reiniciar o Sistema**
- **URL:** `/reboot_sys`
- **Método:** `POST`
- **Descrição:** Envia um comando para reiniciar o sistema.

**Exemplo de Requisição:**
```bash
curl -X POST http://localhost:5000/reboot_sys
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "message": "Sistema será reiniciado."
}
```

---

### **5. Gerenciamento de Blacklist/Whitelist**

#### **Editar Blacklist**
- **URL:** `/blacklist_edit`
- **Método:** `POST`
- **Descrição:** Adiciona ou remove um IP na blacklist.

**Corpo da Requisição (JSON):**
```json
{
    "action": "add",
    "ip": "192.168.0.100"
}
```

**Exemplo de Requisição:**
```bash
curl -X POST -H "Content-Type: application/json"     -d '{"action": "add", "ip": "192.168.0.100"}'     http://localhost:5000/blacklist_edit
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "message": "IP added com sucesso na blacklist."
}
```

#### **Editar Whitelist**
- **URL:** `/whitelist_edit`
- **Método:** `POST`
- **Descrição:** Adiciona ou remove um IP na whitelist.

**Corpo da Requisição (JSON):**
```json
{
    "action": "remove",
    "ip": "192.168.0.50"
}
```

**Exemplo de Requisição:**
```bash
curl -X POST -H "Content-Type: application/json"     -d '{"action": "remove", "ip": "192.168.0.50"}'     http://localhost:5000/whitelist_edit
```

**Resposta de Sucesso (JSON):**
```json
{
    "status": "success",
    "message": "IP removed com sucesso na whitelist."
}
```

---

