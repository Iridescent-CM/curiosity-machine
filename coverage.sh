PYTHONPATH=. DJANGO_SETTINGS_MODULE=curiositymachine.settings coverage run --source . -m py.test && coverage report
