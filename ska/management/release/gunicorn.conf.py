"""Конфигурация Gunicorn для запуска в релиз-режиме"""

import multiprocessing
import os

# Сокет сервера
bind = "127.0.0.1:8000"
backlog = 2048

# Рабочие процессы
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = 'gthread'
worker_tmp_dir = '/dev/shm'

# Таймауты
timeout = 120
keepalive = 5

# Логирование
errorlog = '-'
accesslog = '-'
loglevel = 'info'

# Именование процесса
proc_name = 'ska_release'

# Механика сервера
daemon = False
pidfile = None
umask = 0
user = None
group = None

def on_starting(server):
    """Логирование запуска сервера"""
    server.log.info("Starting release server...")

def on_reload(server):
    """Логирование перезагрузки сервера"""
    server.log.info("Reloading release server...")

def on_exit(server):
    """Логирование остановки сервера"""
    server.log.info("Shutting down release server...")

# Ограничения
max_requests = 1000
max_requests_jitter = 50

# Безопасность
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190 