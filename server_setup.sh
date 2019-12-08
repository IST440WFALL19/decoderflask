#!/bin/bash
# Server Setup script for decoderflask

sudo apt-get update 

sudo apt-get install python-pip python-dev nginx 

sudo pip install virtualenv 

cd /opt/ 

sudo mkdir ist440 

sudo chown ist440 ist440/ 

cd ist440/ 

virtualenv venv 

source venv/bin/activate 

pip install flask uwsgi rq redis

echo '

from app import app 

if __name__ == "__main__": 

    app.run()' > wsgi.py 

echo 'ini 

[uwsgi] 

#python module to import 

module = wsgi:app 

#enable the master process 

master = true 

#spawn number of workers 

processes = 5 

#socket file location 

socket = sampleflask.sock 

#permissions for the socket file 

chmod-socket = 660'  > sampleflask.ini 

sudo echo '#Metadata and dependencies section 

[Unit] 

Description=Decoder service 

After=network.target 

#Define users and app working directory 

[Service] 

User=ist440 

Group=www-data 

WorkingDirectory=/opt/ist440/ 

Environment="PATH=/opt/ist440/venv/bin" 

ExecStart=/opt/ist440/venv/bin/uwsgi --ini sampleflask.ini 

#Link the service to start on multi-user system up 

[Install] 

WantedBy=multi-user.target' > /etc/systemd/system/decoderflask.service 

sudo systemctl start decoderflask 

sudo systemctl status decoderflask 

sudo systemctl enable decoderflask.service 


sudo echo 'server { 

    # the port your site will be served on 

    listen 80; 

    # the IP Address your site will be served on 

    server_name <your_ip>; 

    # Proxy connections to application server 

    location / { 

        include uwsgi_params; 

        uwsgi_pass unix:/opt/ist440/sampleflask.sock; 

    } 

}' > '/etc/nginx/sites-available/decodersite'

sudo ln -s /etc/nginx/sites-available/decodersite /etc/nginx/sites-enabled/ 

sudo systemctl restart nginx 

mkdir /opt/ist440/templates 

cd /opt/ist440/templates 

sudo apt install redis-server 

