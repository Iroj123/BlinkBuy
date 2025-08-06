#!/bin/bash

# wait-for-db.sh

set -e

host="$DB_HOST"
port="$DB_PORT"
user="$DB_USER"
password="$DB_PASSWORD"

echo "Checking environment variables:"
echo "DB_HOST=$host"
echo "DB_PORT=$port"
echo "DB_USER=$user"

export PGPASSWORD="$password"

echo "⏳ Waiting for PostgreSQL at $host:$port with user $user..."

until psql -h "$host" -U "$user" -p "$port" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
  echo "🟡 Still waiting for PostgreSQL at $host:$port... (sleeping)"
  sleep 2
done

echo "✅ PostgreSQL is available!"

# Run the actual command
exec "$@"
