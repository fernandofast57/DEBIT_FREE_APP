
import os
import multiprocessing

# Server socket
bind = '0.0.0.0:8080'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/gunicorn-access.log'
errorlog = 'logs/gunicorn-error.log'
loglevel = 'error'  # Mostra solo errori
capture_output = True
enable_stdio_inheritance = True

# Gestione segnali
ignore_winch = True  # Ignora i segnali di ridimensionamento finestra

# Process naming
proc_name = 'gold-investment'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
