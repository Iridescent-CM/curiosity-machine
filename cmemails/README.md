# Emails

This app handles:

* an old, deprecated `deliver_email` method that 
    * uses event names together with the user type to search for an email template,
		* builds the message and recipient list,
		* creates a Django `EmailMessage`,
		* enqueues a worker job to send it, 
		* and sends it through our Postmark add-on
* new `send` and `subscribe` methods that
    * enqueue worker jobs that issue API calls against Mandrill/Mailchimp
* `mandrill.py` and `mailchimp.py` libraries that encapsulate our interactions with those services
* signal handlers that largely consolidate email-sending logic in one place
* management commands to 
    * work with Mandrill templates
		* send inactive user notifications and manage activity flags
		* send pending example notifications
* and maybe more if something got added without updating this doc!

## Deprecated

The following are deprecated and should be removed when no longer in use:

* `templates/`: templating is now handled within Mailchimp/Mandrill
* `static/`: when templates go, presumably the statics can go
* `mailer.py`: it's a mess 
* `tasks.py`: no longer needed when mailer is gone
* `templates.py`: no longer needed when mailer is gone

Additionally the Postmark add-on should not be needed when the above are all gone, unless
we choose to continue sending simple admin emails through it, which may be useful.

## Mandrill/Mailchimp

Templates are managed in Mailchimp and published to Mandrill. To allow for a
QA process whereby changes go to staging first, `mandrill.py` prepends template
names with the value of a `MANDRILL_TEMPLATE_PREFIX` setting so different
environments can actually send different templates related by a common un-prefixed name.

Our convention at the time of writing this is that staging has no prefix, whereas
production is prefixed by `production-`.

### copy_template

The `copy_template` management command helps automate the process of "promoting"
a template from one prefix (or no prefix) to another, e.g. staging to production.

Run `python manage.py copy_template -h` for a help statement.

### Environments

In addition to staging sending different templates, local development environments make
test API calls that just log in Mandrill without sending any email. You can see test calls
by putting the Mandrill dashboard in [Test mode](https://mandrill.zendesk.com/hc/en-us/articles/205582447-Does-Mandrill-Have-a-Test-Mode-or-Sandbox-).

### Summary

Again, the basic flow is:

* Create or edit a template in Mailchimp
* Publish it to Mandrill
    * The template name will stay the same, and a slug will be created from that
* Optionally set the subject, from address, and from name if not previously set in Mandrill
* Optionally write code that sends the email by referencing the slug name
* Test in staging (or other non-production environment)
    * You may need to put the Mandrill dashboard in test mode, depending on the API key your environment uses
* Copy the template to a template prefixed by the production prefix (`production-` most likely)
to make it live

In general email content should not be edited in Mandrill directly, or the changes could be clobbered
the next time someone publishes from Mailchimp.

## Issues

* Mailchimp and Mandrill allow for templating, but insist on adding a protocol to link URLs. `url_for_template` is a
helper method that prepends the site url to a path, then strips the protocol so it can be used to send dynamic urls
to a template, e.g. `www.curiositymachine.org/page` as `url` + `https://{{ url }}` -> `https://www.curiositymachine.org/page` in the email
* No bulk sending option exists in our library, yet (TODO?)
* Rate-limiting: subscriptions happen currently with an API call per user, so bulk user creation can pose an issue
where we surpass the rate limit for API calls, and users don't get subscribed.
    * at the time of writing this, `skip_welcome_email` and `skip_mailing_list_subscription` flags are checked on 
		the sender object for `created_account` signals