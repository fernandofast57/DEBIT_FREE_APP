# gunicorn.conf.py
import multiprocessing
import os

# Configurazioni base
bind = '0.0.0.0:8080'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'

# Timeouts e limiti
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
errorlog = 'logs/gunicorn-error.log'
accesslog = 'logs/gunicorn-access.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Performance
worker_connections = 1000
threads = 2
backlog = 2048

# Sicurezza
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190


# Hooks per gestione eventi
def on_starting(server):
    """Eseguito quando il server si avvia"""
    server.log.info("Starting Gunicorn server...")
    # Inizializzazione cache o connessioni


def on_exit(server):
    """Eseguito quando il server si ferma"""
    server.log.info("Shutting down Gunicorn server...")
    # Pulizia risorse


def post_fork(server, worker):
    """Eseguito dopo il fork di ogni worker"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def worker_exit(server, worker):
    """Eseguito quando un worker esce"""
    server.log.info(f"Worker exited (pid: {worker.pid})")


def pre_exec(server):
    """Eseguito poco prima di exec() per un worker"""
    server.log.info("Forked child, re-executing.")


# Configurazioni SSL/TLS (se necessario)
keyfile = 'path/to/keyfile'
certfile = 'path/to/certfile'
ssl_version = 'TLS'
