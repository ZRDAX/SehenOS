#!/bin/bash

# Verificar se o script está sendo executado como root
if [[ $EUID -ne 0 ]]; then
    echo "Este script deve ser executado como root" 
    exit 1
fi

SERVICE="postgresql"

#  Parar o serviço postgresql
systemctl stop $SERVICE

# Verificar se o serviço foi configurado corretamente
systemctl status $SERVICE | grep -i "inactive" && echo "Serviço $SERVICE está pausado" || echo "Falha ao pausar o serviço $SERVICE"

# Nome do diretório onde está o docker-compose.yml
PROJECT_DIR="/home/zrdax/SehenOS"

# Entrar no diretório do aprojeto
cd $PROJECT_DIR || { echo "Falha ao acessar o diretório do projeto"; exit 1; }

# Executar o docker-compose up
/usr/local/bin/docker-compose up -d

# Verificar se o comando foi executado corretamente
if [ $? -eq 0 ]; then
    echo "Docker Compose iniciado com sucesso"
else
    echo "Falha ao iniciar Docker Compose"
    exit 1
fi

# Tornar o arquivo executavel
#chmod +x /home/zrdax/SehenOS/scripts/start-docker.sh
