# Curiosity Machine

## Quick Start

Using `pipenv`:

```sh
git clone git@github.com:Iridescent-CM/curiosity-machine.git
cd curiosity-machine
pipenv shell --three
pipenv install --dev
```

Get a .env from another developer and put it in your `curiosity-machine` directory, then

```sh
python manage.py migrate
python manage.py runserver
```

This gets you basically operational. The site won't be terribly intersting with an empty database though.

## Configuration

In development, getting a `.env` from another developer should give you reasonable configuration defaults
to run the app locally.

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

## Requirements

Requirements are managed with `pipenv` and listed in the `Pipfile`.

### When Requirements Get Added

From time to time requirements will get added, updated, or removed from the project. In this case running
the following command should get your environment up to date:

```sh
pipenv install
```

## Data

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

## Job Queues

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

## Project conventions

We don't have a ton of formal conventions, outside of "be reasonable", but we have one in particular to document here for now.

### Template formatting

For indendation, I like the advice [in this conversation](http://stackoverflow.com/questions/18456549/django-template-indentation-guideline#answer-31034928):

1. Django tag does NOT increase the indentation level
2. HTML tag does increase the indentation level

If template logic is complicated enough to be hard to read without additional indentation, it probably belongs in the view, not the template.

## Tests

Run `make test` to run tests.

Test coverage can be generated with `make coverage` or `coverage.sh` for a command-line report,
or to generate an HTML report in `./htmlcov/index.html` use `make cov` or `make htmlcov`.

### Validating HTML

To validate HTML while running tests or using the app, set ```DEBUG_HTML=1``` in your environment to turn on `django-html-validator`.

By default it is configured here to expect a local validation server to be running at port 8888. Download the validator jar
from https://github.com/validator/validator/releases and run it with `java -cp /path/to/vnu.jar nu.validator.servlet.Main 8888` where `/path/to/vnu.jar` is the path to wherever you've put the downloaded jar file. Validation
output will dump to stdout.

## Error Pages

Error pages under `curiositymachine/static/errors/` can be used on Heroku as specified [here](https://devcenter.heroku.com/articles/error-pages).

## Stylesheets

Curiosity Machine is currently using two stylesheet libraries simultaneously. Older pages reference Bootstrap v3 in `curiositymachine/static/less` and newer pages reference Bootstrap v4.0.0-alpha.5 in `curiositymachine/sass`. Ideally, new pages and re-designs of existing pages will all reference the newer sass files and eventually phase out the older less files.

Each library has its own base template that new pages on CM extend:

- New: `{% extends "curiositymachine/layout/base.html" %}`
- Old: `{% extends 'deprecated_base.html' %}`

Visually, you can tell the difference between “old” and “new” templates by whether or not there is a dark `body` containing the page content. Newer pages do _not_ have this. (Currently, most of the pages on Curiosity Machine reference the newer template, the main exception being the engineering design process pages.)

### Header & footer

The header and footer are visually consistent across both old and new templates. Consequently when they change, they need to be updated in two places.

- New header: `curiositymachine/templates/curiositymachine/layout/_header.html`
- New footer: `curiositymachine/templates/curiositymachine/layout/_footer.html`
- Old header: `curiositymachine/templates/_user_nav.html`
- Old footer: inside `curiositymachine/templates/base.html`
