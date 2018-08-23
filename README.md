# Fox Hunting

Fox Hunting is a logical game. The goal of the game is to find all foxes located on the field.

To start the game, click on any square of the field (make a "shot") to open it. If the square is occupied by a fox - it is a "hit". Otherwise, the square contains the number of foxes that are on the lines (horizontal, vertical and diagonals) that cross this square.

![Example](app/static/img/help_example.png)

Find all the foxes in as few moves as possible.

For the first time the idea of the game was published in an article by A. Neschetnyi in “Nauka I Zhisn” (Science and Life) magazine in 1985.

Demo: <http://vps561804.ovh.net/>

## Screenshot

![Screenshot](app/static/img/screenshot.png)

## Requirements

- Python 3.x
- Flask, SQLAlchemy, mysql-connector, gunicorn

## Installation

Clone the app from GitHub and install dependencies in venv:
```
$ git clone https://github.com/alturus/fox_hunting.git
$ python36 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
Create the database:
```
mysql> CREATE DATABASE fox_hunting CHARACTER SET = 'utf8' COLLATE = 'utf8_general_ci';
mysql> CREATE USER 'fox_hunting'@'localhost' IDENTIFIED by 'password';
mysql> GRANT ALL PRIVILEGES ON fox_hunting.* to 'fox_hunting'@'localhost';
```
Create `.env` file with the credentials to connect to the database. For example:
```
FLASK_CONFIG=unix
DATABASE_URL='mysql+mysqlconnector://fox_hunting:password@localhost/fox_hunting'
```
To create the required table in the database, execute:
```
$ flask deploy
```

### nginx

Configure nginx as a proxy server:
```
$ sudo vi /etc/nginx/conf.d/fox_hunting.conf
```
Example of the configuration:
```
server {
    listen 80;
    server_name webserver1;
    access_log  /var/log/nginx/fox_hunting.log;

    location / {
        proxy_pass http://localhost:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
```
`proxy_pass` directive must be the same port on which the gunicorn process is listening.

Check the configuration and restart the nginx web server:
```
$ sudo nginx -t
$ sudo service nginx restart
```

### Supervisor

To automatically start and restart the gunicorn with our application:
```
$ sudo vi /etc/supervisord.d/fox_hunting.ini
```
```
[program:fox_hunting]
directory=/home/web/fox_hunting
command=/home/web/fox_hunting/venv/bin/gunicorn fox_hunting:app -b localhost:8008
autostart=true
autorestart=true
stderr_logfile=/var/log/fox_hunting/fox_hunting.err.log
stdout_logfile=/var/log/fox_hunting/fox_hunting.out.log
```
To enable the configuration, execute:
```
$ sudo supervisorctl reread
$ sudo service supervisor restart
$ sudo supervisorctl status
```
