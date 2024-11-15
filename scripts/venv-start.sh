#!/bin/bash

# Caminho para o ambiente virtual
VENV_PATH="/home/zrdax/test/.venv/bin/activate"

# Verificar se o arquivo de ativação existe
if [ -f "$VENV_PATH" ]; then
    # Ativar o ambiente virtual
    source "$VENV_PATH"
    echo "Ambiente virtual ativado com sucesso."
else
    echo "O caminho para o ambiente virtual não foi encontrado: $VENV_PATH"
fi
