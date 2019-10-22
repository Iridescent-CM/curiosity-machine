# Surveys

This app handles Surveymonkey integration. Here are some notes on how to configure
Surveymonkey and CM to make it work.

This doc applies to the code at b7ddb046fc70d0acd5c73bf253dc450bd38a4f3e.

## The Big Picture

A typical scenario for survey integration is something like the following:

We have a survey set up in Surveymonkey, and we want to direct users on the platform to take it at a
certain point in their user flow on the site. The platform then needs to know a few things: that this survey
exists, whether or not a particular user has taken it, and how to send the user to that survey if necessary.
Furthermore the integration should be able to handle multiple different surveys being used in
different contexts: a pre-survey, a post-survey, etc. And we want to connect survey responses in Surveymonkey
back to users on the platform, when necessary.

### The basic mechanics

To accomplish the above requirements, we have a few moving pieces to coordinate:

* a `Survey` object
* a `SurveyResponse` model with a `ResponseStatus`
* some configuration on the platform side
* some configuration on the Surveymonkey side
* an optional webhook view
* an optional redirect view
* a `Responder` role
* a management command

The `Survey` object is the platform counterpart to a survey in Surveymonkey. It reads what it needs from config based on
a naming convention between config and code, and it knows how to look up a `SurveyResponse` for a particular user. That
`SurveyResponse` represents the response status of a particular user on a particular survey, and defaults to "UNKNOWN".

Each `SurveyResponse` has its own survey url. The `Survey` defines the base url, which points to a *collector* on the
survey in Surveymonkey. Two query parameters specific to the user in question are added by the `SurveyResponse`:`uid` and
`cmtoken`. (The name of `cmtoken` can be changed through config, but that's the default.) The survey must be configured
in Surveymonkey to accept these *custom variables* for integration to work.

When a user completes a survey, one of two things can happen. Typically we redirect users back to the platform to a
specific *redirect view* that marks the relevant `SurveyResponse` as complete before redirecting the user somewhere on the
platform. A second option is to configure a *webhook* on the survey so that Surveymonkey can asynchronously let the
platform know that a user has completed their survey (although it often takes a few seconds). Both approaches can be
used together for extra robustness.

When the platform is notified through either means that a survey has been completed by a user, actions can be taken
specific to the user type or survey by writing a `Responder` for that user type.

And finally, there's a *management command* available that aims to help with all of this: finding IDs, configuring webhooks,
and so forth. See `python manage.py surveymonkey -h` for a help statement, or consult the more detailed documentation
below.

### Survey setup checklist

-[ ] The name of the survey in Surveymonkey is _ _ _ _ _ _ .
-[ ] It has been configured with the `cmtoken` and `uid` custom variables.
-[ ] You have a collector for the survey.
-[ ] The collector has "Multiple Responses" turned **on**.
-[ ] The survey key in the codebase is _ _ _ _ _ _ .
-[ ] You have set `SURVEY_<your key>_LINK` to the collector URL, without query parameters.

Additional config:
-[ ] Does the codebase expect additional config for your survey? E.g. `SURVEY_<your key>_ACTIVE=1`. If so, set it.

If you're redirecting users back to the platform:
-[ ] The survey collector has been configured with a custom "Survey End Page" pointing back to the app.
-[ ] You have set `SURVEY_<your key>_REDIRECT` and/or `SURVEY_<your key>_MESSAGE` as appropriate.

If you're relying on the webhook:
-[ ] Does the environment in question have a webhook? If not, create it.
-[ ] Does the webhook know about your survey? If not, add it.

## The details

### Configuring a Survey on CM

`surveys.get_survey` returns a `Survey` object that loads values from configuration settings. Those settings
take the basic format of `SURVEY_<id>_<attr>`, e.g.

```
SURVEY_SOME_SURVEY_ACTIVE=1
SURVEY_SOME_SURVEY_LINK="http://surveymonkey/whatever"
```

`SURVEY_<id>_LINK` is the only required configuration as far as `SurveyResponse` is concerned,
and should be the survey link **without** the token parameters.

The id can really be anything unique from other configured surveys, but a short descriptive name is good.

### Using in code

There's no general purpose survey middleware yet; see `families/middleware.py` for how family pre-surveys
are handled for an example of how the middleware can work. It additionally wants `SURVEY_<id>_ACTIVE` to be
set to toggle the interrupt on or off. Here's the general idea:

```
survey = get_survey('SOME_SURVEY')
if survey.active:
    response = post_survey.response(request.user)
    if not response.completed:
	... INTERRUPT THE USER ...
	... TYPICALLY show a page that includes the users's link to the survey ...
```

`post_survey.response(request.user)` in the above example automatically creates the `SurveyResponse` connecting
`request.user` to the `post_survey` Survey on its first invocation.

### Survey completion

When a user completes a survey, CM gets notified either by webhook or by redirecting them back to a particular url.

#### Configuring the webhook

There are two possibilities here:

1. you need to create a new webhook for the environment
2. you need to add your survey to an existing webhook for the environment

Use `python manage.py surveymonkey webhooks` to see the available webhooks, and
`python manage.py surveymonkey webhooks --id <id>` to see which surveys the webhook watches,
and which `subscription_url` it will notify of changes.

##### Creating

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

##### Reconfiguring

**The new way**:
If a webhook for your environment exists, you can add your survey to it with the
`surveymonkey webhooks --id <webhook id> --add-survey <survey id>` or
`surveymonkey webhooks --id <webhook id> --remove-survey <survey id>` management commands.

**The old way**:

If a webhook for your environment exists, you can add your survey to it by modifying
`objects_ids` with `python manage.py surveymonkey webhooks --patch '{"object_ids":[...]}'`.
Don't forget to include any old survey ids that are still relevant, while adding your
new id as well.

##### A note on how it works

The webhook does *not* rely on any particular configuration conventions to be followed. Instead it relies
on matching the `SURVEYMONKEY_TOKEN_VAR` value stored in SurveyMonkey as a custom variable, and stored
in the CM instance as a SurveyResponse id. That allows direct lookup of the SurveyResponse, as opposed to
the redirect method which relies on the survey id and identity of the current user to find a SurveyResponse.

#### Configuring a redirect

On the Web Link Collector, modify the Survey End Page. Choose the custom end page option, and
set it to something like `https://www.curiositymachine.org/surveys/completed/`. Surveymonkey will append
the `cmtoken` query param sent across originally, letting the platfrom look up the `SurveyResponse`
directly, without putting the Survey key in the url (as used to be required).

You can set `SURVEY_SOME_SURVEY_REDIRECT=<app:view_name>` to specify where to redirect, or otherwise the user
will be redirect to their dashboard upon returning to CM after completing their survey this way.

You can optionally configure `SURVEY_SOME_SURVEY_MESSAGE=some text here` to include a success message on
the page targetted by the redirection (if it shows messages).

### Additional Surveymonkey considerations

Setting up a survey is outside the scope of this document, but assuming you have your survey written, step
one is to give it the necessary custom variables. You need two. For the first, make sure the name matches the
value of `SURVEYMONKEY_TOKEN_VAR`, which defaults to `cmtoken`. The second is `uid`. Then set up a
web link collector and make note of the URL.

Note that as of 10/3/18, Website Collectors only allow taking a survey once per **browser**, so we do not
use it as some of our users share browsers to access CM.

Make sure in your Web Link Collector that *Multiple Responses* is "On". Otherwise users sharing computers will
only be able to take the survey *once per computer*, not once per user.

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