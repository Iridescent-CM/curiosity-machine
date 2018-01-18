# Surveys

This app handles Surveymonkey integration. Here are some notes on how to configure
Surveymonkey and CM to make it work.

This doc applies to the code at b7ddb046fc70d0acd5c73bf253dc450bd38a4f3e.

## Overview

The general idea is

* user creates account
* middleware `get_or_create`s a SurveyResponse for that user for the required survey
* middleware detects that that SurveyResponse is not complete, and shows the user a url
* that url is a url for the Surveymonkey survey with a custom token variable
* user follows the link and takes the survey
* Surveymonkey has a webhook registered to signal survey completions
* Surveymonkey lets CM know that someone with token X has finished their survey
* CM uses the token to look up the SurveyResponse, mark it as complete
* next time through, the middleware `get_or_create`s the SurveyResponse, sees it is complete, and doesn't intervene

## Configuring CM

`surveys.get_survey` returns a `Survey` object that loads values from configuration settings. Those settings
take the basic format of `SURVEY_<id>_<attr>`, e.g.

```
SURVEY_123_ACTIVE=1
SURVEY_123_LINK="http://surveymonkey/whatever"
```

`SURVEY_<id>_LINK` is the only required configuration as far as `SurveyResponse` is concerned, 
and should be the survey link **without** the token parameters.

The id can really be anything unique from other configured surveys, but using the Surveymonkey survey id
seems like a good idea.

There's no general purpose survey middleware yet; see `families/middleware.py` for how family pre-surveys
are handled for an example of how the middleware can work. It additionally wants `SURVEY_<id>_ACTIVE` to be
set to toggle the interrupt on or off.

## Configuring Surveymonkey

Setting up a survey is outside the scope of this document, but assuming you have your survey written step
one is to give it a custom variable. Make sure the name matches the value of `SURVEYMONKEY_TOKEN_VAR`, which
defaults to `cmtoken`. Set up a web link collector and make note of the URL.

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

## Dev bypass

In development environments, having people fill out dummy surveys and exposing webhook urls
is a pain, so you can also do this:

* set `ALLOW_SURVEY_RESPONSE_HOOK_BYPASS` to True
* configure your survey with link `/surveys/hooks/status/`
* now the link to take the survey will actually hit the webhook url with a `cmtoken` parameter
* the webhook url on GET will check the bypass config, then update the relevant SurveyResponse to completed
* and then redirect to /

Much better!