# Curiosity Machine

## Quick Start

Using `virtualenv` and `virtualenvwrapper`:

```sh
git clone git@github.com:Iridescent-CM/curiosity-machine.git
cd curiosity-machine
mkvirtualenv -a . -r ./requirements.txt -p /path/to/python3 cm
cp sample.local.py curiositymachine/local.py
```

Edit the new `local.py` as appropriate, and

```sh
python manage.py migrate
python manage.py runserver
```

This gets you basically operational. The site won't be terribly intersting with an empty database though.

### Data

One quick way to get going is to clone the Heroku staging database to your local machine and use that, assuming you're
a contributor to the project on Heroku. This can be achieved with the [Heroku Toolbelt](https://toolbelt.heroku.com/) and
the `heroku pg` and `heroku pg:pull` commands.

To use your cloned Postgres database run the app with the following command, substituting in the appropriate user, password, and
database name (or export `DATABASE_URL` to your environment).

```shell
DATABASE_URL=postgres://user:password@localhost:5432/db_name DEBUG=1 python manage.py runserver
```

At this point you'll have content, but be lacking many images. (At least 
until [#87](https://github.com/Iridescent-CM/curiosity-machine/issues/87) gets addressed.)

### Job Queues

Jobs like sending email are handled with [django_rq]. Run redis, then run the following command to launch a worker.

```shell
python manage.py rqworker
```

You can see more about the queues and jobs at `http://localhost:8000/django-rq/` if you log in as an admin.

[django_rq]: http://python-rq.org/patterns/django/

### Scheduled Jobs

It looks like some video-related job can be scheduled. I don't know exactly what it is yet,
so for now I don't run the scheduler.

## Tests

Run `make test` to run tests.

Test coverage can be generated with `make coverage` or `coverage.sh` for a command-line report,
or to generate an HTML report in `./htmlcov/index.html` use `make cov` or `make htmlcov`.
