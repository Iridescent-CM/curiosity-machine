import csv

class MembershipReport():
    def __init__(self, membership):
        self.membership = membership

    def write(self, fp):
        fp.write("educators\r\n")
        self._write_educators(fp)
        fp.write("\r\nstudents\r\n")
        self._write_students(fp)
        fp.write("\r\nchallenges\r\n")
        self._write_challenges(fp)

    def _write_educators(self, fp):
        headers = ['id', 'username', 'email', 'first_name', 'last_name']
        writer = csv.DictWriter(fp, headers)
        writer.writeheader()
        for d in self.membership.educators.values(*headers).all():
            writer.writerow(d)

    def _write_students(self, fp):
        headers = ['id', 'username', 'email', 'first_name', 'last_name']
        writer = csv.DictWriter(fp, headers)
        writer.writeheader()
        for d in self.membership.students.values(*headers).all():
            writer.writerow(d)

    def _write_challenges(self, fp):
        headers = ['id', 'name']
        writer = csv.DictWriter(fp, headers)
        writer.writeheader()
        for d in self.membership.challenges.values(*headers).all():
            writer.writerow(d)
