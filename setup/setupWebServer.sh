#!usr/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

ip=$(wget http://ipinfo.io/ip -qO -)

echo "$ip"

echo PYTHON ENVIRONMENT
sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
sudo pip3 install virtualenv
mkdir ~/myproject
cd ~/myproject
virtualenv myprojectenv
source myprojectenv/bin/activate
pip install gunicorn flask

echo "from flask import Flask
app = Flask(__name__)

@app.route(\"/\")
def hello():
    return \"<h1 style='color:blue'>Hello World!</h1>\"

if __name__ == \"__main__\":
    app.run(host='0.0.0.0')" > ~/myproject/myproject.py

echo GUNICORN CONFIG

echo "from myproject import app

if __name__ == \"__main__\":
    app.run()" > ~/myproject/wsgi.py

deactivate

echo SYSTEMD Unit File
echo "[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myproject
Environment=\"PATH=/home/ubuntu/myproject/myprojectenv/bin\"
ExecStart=/home/ubuntu/myproject/myprojectenv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/myproject.service

sudo systemctl start myproject
sudo systemctl enable myproject

echo "server {
    listen 80;
    server_name $ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/myproject/myproject.sock;
    }
}" > /etc/nginx/sites-available/myproject

sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

echo "python myproject.py to test flask app"
echo "gunicorn --bind 0.0.0.0:5000 wsgi:app to test gunicorn"
echo "sudo nginx -t to test Nginx"
