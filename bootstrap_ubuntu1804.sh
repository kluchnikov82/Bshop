#!/bin/sh -e

PG_VERSION=10

# pg ppa
PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list

echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > "$PG_REPO_APT_SOURCE"
# Add PGDG repo key:
wget --quiet -O - https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -


# rabbit ppa
echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -

# node  ppa
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -    

apt update
apt upgrade -y        
apt  install -y libpq-dev python3-dev python3-pip supervisor tree \
  postgresql-$PG_VERSION postgresql-contrib-$PG_VERSION \
  rabbitmq-server \
  nodejs

# pipenv
pip3 install pipenv
su - vagrant -c "cd /opt/bshop/backend && pipenv install"    

# su - vagrant -c "cd /opt/bshop/frontend && npm install" 

## pgsql

PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Edit postgresql.conf to change listen address to '*':
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

# Restart so that all new config is loaded:
service postgresql restart


cat << EOF | su - postgres -c psql

ALTER USER postgres WITH PASSWORD 'postgres';

EOF

su - postgres -c "psql -f /opt/bshop/db/bshop-dump.sql"    

reboot
