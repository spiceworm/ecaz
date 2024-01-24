import multiprocessing
import os

bind = "0.0.0.0:8081"
chdir = "/app"

if os.environ["PROD"] == "1":
    workers = multiprocessing.cpu_count() * 2 + 1
else:
    reload = True
    workers = 1
