# HelloSign

## Configuration

### API

* `HELLOSIGN_API_KEY`
* `HELLOSIGN_PRODUCTION_MODE`: defaults to False, in production mode signed forms are legally binding

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