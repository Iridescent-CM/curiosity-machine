# Curiosity Machine

## Quick Start

Using `virtualenv` and `virtualenvwrapper`:

```shell
git clone git@github.com:Iridescent-CM/curiosity-machine.git
cd curiosity-machine
mkvirtualenv -a . -r ./requirements.txt -p /path/to/python3 cm
python manage.py migrate
DEBUG=1 python manage.py runserver
```

This gets you partially operational. The site won't be terribly intersting with an empty database,
and things like sending email after signup will explode.

### Database

One quick way to get going is to clone the Heroku staging database to your local machine and use that, assuming you're
a contributor to the project on Heroku. This can be achieved with the [Heroku Toolbelt](https://toolbelt.heroku.com/) and
the `heroku pg` and `heroku pg:pull` commands.

To use your cloned Postgres database run the app with the following command, substituting in the appropriate user, password, and
database name (or export `DATABASE_URL` to your environment).

```shell
DATABASE_URL=postgres://user:password@localhost:5432/db_name DEBUG=1 python manage.py runserver
```

At this point you'll have content, but be lacking many images. Also, signup will still explode.

### Sign-up Email

Jobs like sending email are handled with [django_rq]. Run redis, then run the following command to launch a worker.

```shell
python manage.py rqworker
```

Now signup should proceed locally, though you won't get a signup email and the logs will probably show
that sending the email exploded with `smtplib.SMTPServerDisconnected: please run connect() first`. But that's
better than the app crashing.

You can see more about the queues and jobs at `http://localhost:8000/django-rq/` if you log in as an admin.

[django_rq]: http://python-rq.org/patterns/django/

### Scheduled Jobs

It looks like some video-related job can be scheduled. I don't know exactly what it is yet,
so for now I don't run the scheduler.

## Tests

Run `make test` to run tests.

Test coverage can be generated with `make coverage` or `coverage.sh` for a command-line report,
or to generate an HTML report in `./htmlcov/index.html` use `make cov` or `make htmlcov`.
