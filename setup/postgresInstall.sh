#!/bin/bash

# install new postgres database server
echo "Installing Postgres"
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

echo "sudo -u postgres psql <- to connect to database"
echo "sudo -u postgres <- to become postgres user, exit to logout"
echo "\conninfo <- for connection info (database name, user, socket, port)"
echo "\q <- to disconnect"


echo "Installing SQLAlchemy and psycopg2 into conda environment"
conda install psycopg2
conda install -c conda-forge flask-sqlalchemy
conda install -c conda-forge flask-migrate 
