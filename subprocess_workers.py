import os
try:
    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
except Exception:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'curiositymachine.settings'

from subprocess import Popen
import signal
import time
from django_rq import get_scheduler

NUMBER_OF_WORKERS = 4

commands = ['python -u manage.py rqworker'] * NUMBER_OF_WORKERS

processes = [Popen(cmd, shell=True) for cmd in commands]

def handler(signum, frame):
    print("Caught SIGTERM, raising SystemExit")
    raise SystemExit("SystemExit from SIGTERM")

signal.signal(signal.SIGTERM, handler)

wait_length = 10

while True:
    try:
        time.sleep(wait_length) # starting the scheduler fails if another one is running, so give it time for the old one's connection to break cleanly
        scheduler = get_scheduler(name='default', interval=10)
        print("Starting scheduler")
        scheduler.run()
    except ValueError:
        print("Scheduler failed to start, will retry")
        wait_length = 120
        continue # if it looks like another scheduler is still running, go ahead and wait and try again.  If there actually is another scheduler running and this happens forever, there's no great loss. (If that is the expected case, maybe remove the print statement in this block)
    except (SystemExit, KeyboardInterrupt):
        print("Caught signal, terminating workers and scheduler")
        for p in processes: p.terminate()
        break

for p in processes: p.wait() # subprocesses will terminate once their current jobs are done
