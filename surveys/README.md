# Surveys

This app handles Surveymonkey integration. Here are some notes on how to configure
Surveymonkey and CM to make it work.

This doc applies to the code at b7ddb046fc70d0acd5c73bf253dc450bd38a4f3e.

## Configuring on CM

`surveys.get_survey` returns a `Survey` object that loads values from configuration settings. Those settings
take the basic format of `SURVEY_<id>_<attr>`, e.g.

```
SURVEY_123_ACTIVE=1
SURVEY_123_LINK="http://surveymonkey/whatever"
```

`SURVEY_<id>_LINK` is the only required configuration as far as `SurveyResponse` is concerned,
and should be the survey link **without** the token parameters.

The id can really be anything unique from other configured surveys, but using the Surveymonkey survey id
is an easy way to go. Note that this naming scheme won't work if you want the same survey delivered
multiple times depending on the context, in which case you'll need differing ids pointing to the same
survey link.

## Configuring in Surveymonkey

Setting up a survey is outside the scope of this document, but assuming you have your survey written, step
one is to give it a custom variable. Make sure the name matches the value of `SURVEYMONKEY_TOKEN_VAR`, which
defaults to `cmtoken`. Set up a web link collector and make note of the URL.

Note that as of 10/3/18, Website Collectors only allow taking a survey once per **browser**, so we do not
use it as some of our users share browsers to access CM.

## Using in code

There's no general purpose survey middleware yet; see `families/middleware.py` for how family pre-surveys
are handled for an example of how the middleware can work. It additionally wants `SURVEY_<id>_ACTIVE` to be
set to toggle the interrupt on or off. Here's the general idea:

```
survey = get_survey(settings.SOME_SURVEY_ID)
if survey.active:
    response = post_survey.response(request.user)
    if not response.completed:
	... INTERRUPT THE USER ...
```

## Survey completion

When a user completes a survey, CM gets notified either by webhook or by redirecting them back to a particular url.

### Configuring the webhook

There are two possibilities here:

1. you need to create a new webhook for the environment
2. you need to add your survey to an existing webhook for the environment

Use `python manage.py surveymonkey webhooks` to see the available webhooks, and
`python manage.py surveymonkey webhooks --id <id>` to see which surveys the webhook watches,
and which `subscription_url` it will notify of changes.

#### Creating

Use `python manage.py surveymonkey webhooks --post '{...}'` to create a new webhook. The following
should be a reasonable template for the POST data:

```
{
  'event_type': 'response_completed',
  'name': 'Webhook for env',
  'object_ids': ['123', '456'],
  'object_type': 'survey',
  'subscription_url': 'http://url-for-env.org/surveys/hooks/status/'
}
```

The `object_ids` are the survey ids for which you want updates. Use `python manage.py surveys` and
its related options to find those.

#### Reconfiguring

If a webhook for your environment exists, you can add your survey to it by modifying
`objects_ids` with `python manage.py surveymonkey webhooks --patch '{"object_ids":[...]}'`.
Don't forget to include any old survey ids that are still relevant, while adding your
new id as well.

### Configuring a redirect

On the Web Link Collector, modify the Survey End Page. Choose the custom end page option, and
set it to something like `https://www.curiositymachine.org/surveys/123/completed/`, if for example
your survey ID was 123.

You can set `SURVEY_123_REDIRECT=<app:view_name>` to specify where to redirect, or otherwise the user
will be redirect to their dashboard upon returning to CM after completing their survey this way.

### Running code on survey completion

When CM is notified of the completion of a survey, it will attempt to load `surveys.Responder` from the
app corresponding to the user's set role. See `surveys/updating.py` and `families/surveys.py` for details
and an example of taking an action upon survey completion.

## Dev bypass

In development environments, having people fill out dummy surveys and exposing webhook urls
is a pain, so you can also do this:

* set `ALLOW_SURVEY_RESPONSE_HOOK_BYPASS` to True
* configure your survey with link `/surveys/hooks/status/`
* now the link to take the survey will actually hit the webhook url with a `cmtoken` parameter
* the webhook url on GET will check the bypass config, then update the relevant SurveyResponse to completed
* and then redirect to /

Much better!