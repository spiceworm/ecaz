import multiprocessing
import os

bind = "0.0.0.0:8081"
chdir = "/app"

if "PROD" in os.environ:
    workers = multiprocessing.cpu_count() * 2 + 1
else:
    reload = True
    workers = 1
