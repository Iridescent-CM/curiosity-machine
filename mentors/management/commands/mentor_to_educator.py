from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from challenges.models import Progress
from educators.models import EducatorProfile
from profiles.models import UserRole

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        successes = 0
        errored_ids = []
        non_mentors = []

        for id in options['id']:
            self.stdout.write('\nID %d' % id)
            u = get_user_model().objects.get(pk=id)

            if not hasattr(u, 'mentorprofile'):
                self.stdout.write('User id=%d has no Mentor profile' % id)
                non_mentors.append(id)
                continue

            self.stdout.write('Converting user id=%d' % id)

            deleted = u.notifications.all().delete()
            self.stdout.write('\tDeleting notifications')

            progresses = Progress.objects.filter(mentor=u)
            self.stdout.write('\tUnsetting as mentor on progresses')
            progresses.update(mentor_id=None)

            old_profile = u.mentorprofile

            if not hasattr(u, 'educatorprofile'):
                self.stdout.write('\tCreating educator profile')
                new_profile = EducatorProfile(
                    user=u,
                    image=old_profile.image,
                    organization=old_profile.employer
                )
                try:
                    new_profile.full_clean(exclude=['location'])
                    new_profile.save()
                except ValidationError as e:
                    self.stdout.write('\tEncountered validation error, please fix and try again')
                    errored_ids.append(id) 
                    continue

            self.stdout.write('\tSetting role to Educator')
            u.extra.role = UserRole.educator.value
            u.extra.save()

            self.stdout.write('\tDeleting mentor profile')
            old_profile.delete()
            successes += 1

        self.stdout.write('\n---\nMentors converted: %d' % successes)
        self.stdout.write('Mentors with errors: %d' % len(errored_ids))
        self.stdout.write('\tIDs: %s' % ' '.join([str(i) for i in errored_ids]))
        self.stdout.write('Non-mentors: %d' % len(non_mentors))
        self.stdout.write('\tIDs: %s' % ' '.join([str(i) for i in non_mentors]))