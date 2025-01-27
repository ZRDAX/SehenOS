#!/bin/bash

# Verificar se o script está sendo executado como root
if [[ $EUID -ne 0 ]]; then
    echo "Este script deve ser executado como root" 
    exit 1
fi

# Interface de rede que será colocada em modo promíscuo
INTERFACE="eth0"

# Colocar a interface em modo promíscuo
ip link set $INTERFACE promisc on

# Verificar se a interface foi configurada corretamente
ip addr show $INTERFACE | grep -i "PROMISC" && echo "Interface $INTERFACE está em modo promíscuo" || echo "Falha ao configurar a interface $INTERFACE"
