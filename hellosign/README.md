# HelloSign

## Configuration

### API

* `HELLOSIGN_API_KEY`
* `HELLOSIGN_PRODUCTION_MODE`: Defaults to False, in production mode signed forms are legally binding
* `HELLOSIGN_ENVIRONMENT_NAME`: Arbitrary name used to match completed signature requests with the
environment the requests came from, should not be changed if there are pending requests from your
environment. Should be unique for production environments.

### Management commands

* `approve_student_profiles`: To be documented, has specific config to be documented as well.
* `update_signatures`: Run with template id(s), will search for signed requests and update
the relevant Signature models.

### HelloSign Templates

* `HELLOSIGN_TEMPLATE_<uppercase name>_ID`: HelloSign ID of template
* `HELLOSIGN_TEMPLATE_<uppercase name>_SIGNER_ROLE`: Optional, defaults to "Parent"
* `HELLOSIGN_TEMPLATE_<uppercase name>_EMAIL_ID`: Required if template auto-populates email
* `HELLOSIGN_TEMPLATE_<uppercase name>_USERNAME_ID`: Required if template auto-populates username
* `HELLOSIGN_TEMPLATE_<uppercase name>_BIRTHDAY_ID`: Required if template auto-populates birthday

### Specific Templates

Specific templates may require additional settings based on how they're used in the code. In general,
`HELLOSIGN_TEMPLATE_<uppercase name>_SETTING_NAME=value` will make "value" available as
`ConsentTemplate(<ID>).setting_name` (given the correct ID).

#### Family consent template

* `AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID`: ID of family consent template, which should be configured as above.
* `HELLOSIGN_TEMPLATE_<family consent name>_ACTIVE`: defaults to False, set to turn on consent form check

### Django Templates

For each HelloSign template, two Django templates should exist:

* `hellosign/emails/<lowercase name>_subject.txt`: Subject for HelloSign signature request email
* `hellosign/emails/<lowercase name>_message.txt`: Text body for HelloSign signature request email