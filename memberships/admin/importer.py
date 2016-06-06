import csv

from profiles.forms.student import StudentUserAndProfileForm

def decode_lines(f, encoding='utf-8'):
    for line in f:
        yield line.decode(encoding)

class Importer(object):
    """
    Importer takes a csv and creates member objects for confirmation or
    actual (bulk) creation. The csv is assumed to be small enough to fit
    comfortably in memory, with ImportForm should guarantee.
    """

    def parse(self, f):
        contents = f.read().decode('utf-8')
        f.seek(0)
        dialect = csv.Sniffer().sniff(contents)
        reader = csv.DictReader(decode_lines(f))

        from django.forms.models import modelformset_factory
        from django.contrib.auth.models import User
        MyFormset = modelformset_factory(User, StudentUserAndProfileForm)
        data = {}
        idx = 0
        for row in reader:
            row["confirm_password"] = row["password"]
            data.update({"form-%d-%s" % (idx, k): v for k, v in row.items()})
            idx += 1
        data.update({
             'form-TOTAL_FORMS': idx,
             'form-INITIAL_FORMS': '0',
             'form-MAX_NUM_FORMS': '',
        })
        f = MyFormset(data=data)
        return f
