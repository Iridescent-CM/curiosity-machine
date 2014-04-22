from subprocess import Popen

NUMBER_OF_WORKERS = 8

commands = ['python manage.py rqworker'] * NUMBER_OF_WORKERS
commands += ['python manage.py rqscheduler']

processes = [Popen(cmd, shell=True) for cmd in commands]

for p in processes: p.wait()
