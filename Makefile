test:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=curiositymachine.test_settings py.test 

coverage:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=curiositymachine.test_settings coverage run --source . -m py.test && coverage report

cov:
	rm -rf htmlcov
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=curiositymachine.test_settings coverage run --source . -m py.test && coverage html

clean:
	rm -rf htmlcov

fixtures:
	python manage.py loaddata basic-users basic-challenges progress-basic-challenges basic-filters basic-units basic-groups themes