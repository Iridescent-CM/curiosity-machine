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

## Configuration

In development, copying `sample.local.py` to `curiositymachine/local.py` hopefully provides a reasonable starting point,
although it has the tendency to lag behind the current state of the app config. Please issue pull requests with fixes
and improvements as you realize they are needed.

### Environment variables

`curiositymachine/settings.py` contains the full app config with some amount of commentary. Many settings are
pulled from environment variables as we do not use environment-specific configuration files outside of development.
Some of those variables allow the case-insensitive word "false" to count as False, though it's recommended to use
the empty string for false and "1" to mean true, which will work if that additional parameter processing gets removed.

### Feature flags

Also, as mentioned in that file, we have a pattern for feature flags where variables beginning with `ENABLE_`
are processed into a `FEATURE_FLAGS` dictionary and made available throughout the project to toggle different
behavior. Your best bet to see what feature flags the code currently relies on is to grep for it, or something similar:

```console
$ grep -ir --include .*py --include .*html --exclude-dir node_modules enable_ .`
```

## When Requirements Get Added

From time to time requirements will get added, updated, or removed from the project. In this case running
the following command should get your environment up to date:

```sh
pip install -r requirements.txt
```

### Data

One quick way to get going is to clone the Heroku staging database to your local machine and use that, assuming you're
a contributor to the project on Heroku. This can be achieved with the [Heroku Toolbelt](https://toolbelt.heroku.com/) and
the `heroku pg` and `heroku pg:pull` commands.

To use your cloned Postgres database run the app with the following command, substituting in the appropriate user, password, and
database name (or export `DATABASE_URL` to your environment).

```sh
DATABASE_URL=postgres://user:password@localhost:5432/db_name DEBUG=1 python manage.py runserver
```

At this point you'll have content, but be lacking many images. (At least
until [#87](https://github.com/Iridescent-CM/curiosity-machine/issues/87) gets addressed.)

### Job Queues

Jobs like sending email are handled with [django_rq].
Run redis, then run the following command to launch a worker.

```sh
python manage.py rqworker
```

You can see more about the queues and jobs at `http://localhost:8000/django-rq/` if you log in as an admin.

[django_rq]: http://python-rq.org/patterns/django/

### Scheduled Jobs

Video encoding runs as a scheduled job with [rq-scheduler]. With redis running, you can run the following
command to launch the scheduler and kick off scheduled jobs.

```sh
python manage.py rqscheduler
```

[rq-scheduler]: https://github.com/ui/rq-scheduler

## Tests

Run `make test` to run tests.

Test coverage can be generated with `make coverage` or `coverage.sh` for a command-line report,
or to generate an HTML report in `./htmlcov/index.html` use `make cov` or `make htmlcov`.

## Error Pages

Error pages under `curiositymachine/static/errors/` can be used on Heroku as specified [here](https://devcenter.heroku.com/articles/error-pages).
