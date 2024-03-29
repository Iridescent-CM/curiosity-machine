import os
import time
from subprocess import Popen

NUMBER_OF_WORKERS = int(os.environ.get('RQ_CONCURRENT_WORKERS', 4))
SCHEDULER_CMD = os.environ.get('RQ_SCHEDULER_COMMAND', 'python -u manage.py rqscheduler --queue default -i 10')
WORKER_CMD = os.environ.get('RQ_WORKER_COMMAND', 'python -u manage.py rqworker default --worker-class rq.worker.HerokuWorker')

commands = [SCHEDULER_CMD]
commands += [WORKER_CMD] * NUMBER_OF_WORKERS

processes = [Popen(cmd, shell=True) for cmd in commands]

while True:
    if any([p.poll() != None for p in processes]):
        break   # if any subprocess finishes, terminate the rest so the dyno can restart
    time.sleep(1)

for p in processes: p.terminate()

