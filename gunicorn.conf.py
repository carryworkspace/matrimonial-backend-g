# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 4
worker_class = "gthread"  # You can use 'sync' or 'gevent' depending on your application
timeout = 30
