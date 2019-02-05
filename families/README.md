# Family accounts & AI Family Challenge

## 2018 Overview: first season

The 2018 AIFC is a predefined curriculum divided into three stages. The first two stages
contain Design Challenges and accompanying Units, whereas the third stage is composed
entirely of Lessons.

Families sign up for Family accounts, and are then presented with a dashboard of their progress,
a set of stage tabs outlining the content of each stage, and a World Championship tab that
helps them complete a checklist of items that allows them to access AwardForce, a 3rd party
platform where submissions are built and judging is held (it's essentially where the competition
actually happens).

## Details

### Enrolling

There is no separate enrollment or opt-in for the AIFC for a Family account user. Having a Family
account is taken to mean that you are participating in the season and will (potentially) compete.
This works for 2018 since Family accounts didn't exist prior to the launch of the AIFC, but may not work
in the future as an indicator of interest in the current season.

#### Account creation vs. conversion

Family accounts could be created through 2 different means: creating a new account or converting an
existing one. Converting had the advantage of bringing along completed Design Challenges.

#### Organic vs. in-person users, and Coaches

Many Family accounts came from people enrolled in in-person programs that would take them through
the AIFC curriculum under the guidance of a Coach, which is what we call Educator accounts associated
with a group of AIFC Family account users. These Family account users and Coaches were grouped through
the old Membership feature, so Coaches were able to give feedback on the DCs similarly to how 
Educators could provide feedback to Students. This feedback feature was not extended to Lessons due
to time considerations.

### Curriculum

The first two stages are comprised of Design Challenges. These are not differentiated from the
general CM DCs, so e.g. a student who converted their account would potentially began the season 
with the curriculum partially complete.

The third stage was a set of new items called Lessons. Each lesson is comprised of a series of tabs,
and offers a more Wordpress-like, flexible authoring format through the admin than DCs allow. Each
Lesson includes a Quiz as well as a space to upload media or text, answering questions posed by the
Lesson or allowing for generic feedback.

### Competition submission

Submitting to the AIFC is handled off of this platform, on AwardForce. However CM does try to provide
and easy link over to AwardForce with basic account creation. Family account users have to complete
a checklist of technical items (confirming their email address, taking a survey, etc.) before
they are presented with the button to go to AwardForce.

Eventually this option will be disabled for users who have not already done it, while users with
accounts on AwardForce will continue to see a link that will send them to the submissions platform.

### Preparing for the next season

TBD

## Technical considerations

### Configuration

The curriculum was (partially) configured through:
* `AICHALLENGE_STAGE_1_CHALLENGES`
* `AICHALLENGE_STAGE_1_UNITS`
* `AICHALLENGE_STAGE_2_CHALLENGES`
* `AICHALLENGE_STAGE_2_UNITS`
* Stage 3 was taken at this point to be "all Lessons in the database, in their default order"

Educators signing up as Coaches were automatically added to a "special" AIFC membership through `AICHALLENGE_COACH_MEMBERSHIP_ID`.

Various surveys were delivered to users throughout the season:
* `AICHALLENGE_FAMILY_PRE_SURVEY_ID`
* `AICHALLENGE_COACH_PRE_SURVEY_ID`
* `AICHALLENGE_FAMILY_POST_SURVEY_ID`
* `AICHALLENGE_FAMILY_PRE_SUBMISSION_SURVEY_ID`
* `AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID`

A flag was added late in the game to allow "turning off" of the AwardForce integration as `AIFC_SEASON_OPEN`.

And various `ENABLE_` flags were used for a staged rollout. Probably the most relevant are:
* `ENABLE_AI_BANNER`
* `ENABLE_AIFCWC_TAB`