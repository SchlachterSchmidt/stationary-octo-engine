#!/bin/bash

wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

echo "sudo -u postgres psql <- to connect to database"
echo "sudo -u postgres <- to become postgres user, exit to logout"
echo "\q <- to disconnect"
