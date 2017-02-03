import csv
import re
from django.utils.timezone import now

class MembershipReport():

    dialect = csv.excel

    def __init__(self, membership, dialect=None):
        if dialect:
            self.dialect = csv.get_dialect(dialect)
        self.membership = membership

    @staticmethod
    def build_path(object_id, filename):
        return '/memberships/%s/reports/%s' % (object_id, filename)

    @property
    def path(self):
        return self.build_path(self.membership.id, filename=self.filename)

    @property
    def filename(self):
        name = re.sub('[-\s]+', '-', self.membership.name.strip())
        return name + '.csv'

    def write(self, fp):
        fp.write(self.membership.name + " " + now().strftime('%Y-%m-%d %H:%M:%S'))
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
        headers = ['id', 'username', 'email', 'first_name', 'last_name']
        writer = csv.DictWriter(fp, headers, dialect=self.dialect)
        writer.writeheader()
        for d in self.membership.students.values(*headers).all():
            writer.writerow(d)

    def _write_challenges(self, fp):
        headers = ['id', 'name']
        writer = csv.DictWriter(fp, headers, dialect=self.dialect)
        writer.writeheader()
        for d in self.membership.challenges.values(*headers).all():
            writer.writerow(d)
