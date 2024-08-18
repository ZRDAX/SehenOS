#!/bin/bash
set -e

host="$1"
shift
cmd="$@"

export PGPASSWORD="piswos"  # Define a senha do banco de dados como variável de ambiente

until psql -h "$host" -U "cypher" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
