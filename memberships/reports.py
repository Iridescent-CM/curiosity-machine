import csv
import re
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from challenges.models import Progress

User = get_user_model()

class MembershipReport():

    dialect = csv.excel
    date_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, membership, dialect=None):
        if dialect:
            self.dialect = csv.get_dialect(dialect)
        self.membership = membership

    @staticmethod
    def build_path(object_id, filename):
        return 'memberships/%s/reports/%s' % (object_id, filename)

    @property
    def path(self):
        return self.build_path(self.membership.id, filename=self.filename)

    @property
    def filename(self):
        name = re.sub('[-\s]+', '-', self.membership.name.strip())
        return name + '.csv'

    def write(self, fp):
        fp.write(self.membership.name)
        fp.write(self.dialect.lineterminator)
        fp.write("Report run: " + now().strftime(self.date_format))
        fp.write(self.dialect.lineterminator)
        fp.write("Membership created: " + self.membership.created_at.strftime(self.date_format))
        fp.write(self.dialect.lineterminator)
        fp.write(self.dialect.lineterminator)
        fp.write("educators")
        fp.write(self.dialect.lineterminator)
        self._write_educators(fp)
        fp.write(self.dialect.lineterminator)
        fp.write("students")
        fp.write(self.dialect.lineterminator)
        self._write_students(fp)
        fp.write(self.dialect.lineterminator)
        fp.write("challenges")
        fp.write(self.dialect.lineterminator)
        self._write_challenges(fp)

    def _write_educators(self, fp):
        headers = ['id', 'username', 'email', 'first_name', 'last_name']
        writer = csv.DictWriter(fp, headers, dialect=self.dialect)
        writer.writeheader()
        for d in self.membership.educators.values(*headers).all():
            writer.writerow(d)

    def _write_students(self, fp):
        model_headers = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_headers = ['submissions']
        writer = csv.DictWriter(fp, model_headers + extra_headers, dialect=self.dialect)
        writer.writeheader()
        total = 0
        for d in self.membership.students.values(*model_headers).all():
            d['submissions'] = Progress.objects.filter(
                owner=d["id"],
                comments__user=d["id"],
                challenge__membership=self.membership
            ).distinct().count()
            total += d['submissions']
            writer.writerow(d)
        writer.writerow({'submissions': total})

    def _write_challenges(self, fp):
        headers = ['id', 'name', 'submissions']
        writer = csv.DictWriter(fp, headers, dialect=self.dialect)
        writer.writeheader()
        total = 0
        for d in self.membership.challenges.values('id', 'name').all():
            d['submissions'] = User.objects.filter(
                membership=self.membership.id,
                comment__challenge_progress__challenge=d['id']
            ).distinct().count()
            total += d['submissions']
            writer.writerow(d)
        writer.writerow({'submissions': total})
