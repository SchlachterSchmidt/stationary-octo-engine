#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

ip=$(wget http://ipinfo.io/ip -qO -)
echo "my IP: $ip"

# create project folder
dir=~/finalProject
if [ ! -d  "$dir" ]; then
    mkdir $dir;
fi;
cd $dir

apt-get install nginx

echo ANACONDA ENVIRONMENT
cd ~
wget https://repo.continuum.io/archive/Anaconda3-5.0.0.1-Linux-x86_64.sh
bash Anaconda3-5.0.0.1-Linux-x86_64.sh -b -p ~/anaconda
rm Anaconda3-5.0.0.1-Linux-x86_64.sh
echo 'export PATH="~/anaconda/bin:$PATH"' >> ~/.bashrc
sleep 2
source .bashrc
sleep 3
echo conda installed successfully
echo updating conda packages, press y to confirm
sleep 2
conda update conda
conda update anaconda
conda create -n finalProject python=3.6 anaconda
source activate finalProject
conda install pip numpy scipy theano scikit-learn jupyter flask gunicorn psycopg2 matplotlib nb_conda
conda install -c conda-forge flask-httpauth flask-sqlalchemy flask-script flask-migrate bcolz conda
conda install -c anaconda passlib boto3
conda install -c menpo opencv3
pip install keras coverage

echo CREATING SAMPLE FLASK app

echo "from flask import Flask
app = Flask(__name__)
@app.route(\"/\")
def hello():
    return \"<h1 style='color:blue'>Hello World!</h1>\"
if __name__ == \"__main__\":
    app.run(host='0.0.0.0')" > ~/finalProject/app.py

echo CREATING GUNICORN CONFIG

echo "from app import app
if __name__ == \"__main__\":
    app.run()" > ~/finalProject/wsgi.py


echo DEACTIVATING CONDA ENVIRONMENT
source deactivate

echo SYSTEMD UNIT FILE
echo "[Unit]
Description=Gunicorn instance to serve finalProject
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/finalProject
Environment="PATH=/home/ubuntu/anaconda/finalproject/bin"
ExecStart=/home/ubuntu/anaconda/§finalproject/bin/gunicorn --workers 3 --bind unix:finalProject.sock -m 007 wsgi:app
[Install]
WantedBy=multi-user.target" > /etc/systemd/system/finalProject.service

sudo systemctl start finalProject
sudo systemctl enable finalProject

echo "server {
    listen 80;
    server_name $ip;
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/finalProject/finalProject.sock;
    }
}" > /etc/nginx/sites-available/finalProject

sudo ln -s /etc/nginx/sites-available/finalProject /etc/nginx/sites-enabled
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

echo "python app.py to test flask app"
echo "gunicorn --bind 0.0.0.0:5000 wsgi:app to test gunicorn"
echo "sudo nginx -t to test Nginx"
