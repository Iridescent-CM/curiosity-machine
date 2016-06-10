import csv
from django.db import transaction, DataError

def decode_lines(f, encoding='utf-8'):
    for line in f:
        yield line.decode(encoding)

class BulkImporter(object):
    """
    Given a ModelForm, BulkImporter will create models form the rows of a CSV data file.

    All rows will be checked for validity first, and no models created if an invalid
    row is encountered. Exceptions encountered saving a model will be logged but will not
    prevent creation of other models.

    An output CSV will be generated detailing the records created and the errors or exceptions
    encountered.
    """

    def __init__(self, modelformclass):
        """
        modelformclass -  the ModelForm to use on input rows
        """
        self.modelformclass = modelformclass

    def _open_reader(self, f):
        contents = f.read().decode('utf-8')
        f.seek(0)
        dialect = csv.Sniffer().sniff(contents)
        return csv.DictReader(decode_lines(f))

    def _build_fieldnames(self, keys):
        keys.sort()
        if not "errors" in keys:
            keys.append('errors')
        return keys

    def _format_errors(self, errors):
        return " ".join(["%s: %s" % (k, " ".join(v)) for k, v in iter(sorted(errors.items()))])

    def call(self, infile, outfile):
        """
        infile  -  A readable binary mode file, assumed to be UTF-8 encoded, containing CSV data with header  
        outfile -  A writable text mode file for output
        """
        reader = self._open_reader(infile)

        valid = []
        clean = True
        for idx, row in enumerate(reader):
            if idx == 0:
                fieldnames = self._build_fieldnames(list(row.keys()))
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

            form = self.modelformclass(row)
            if form.is_valid():
                row['errors'] = ''
                valid.append((row, form))
            else:
                row['errors'] = self._format_errors(form.errors)
                writer.writerow(row)
                clean = False

        for row, form in valid:
            if clean:
                try:
                    with transaction.atomic():
                        obj = form.save()
                        writer.writerow(row)
                except Exception as err:
                    row['errors'] = "Exception encountered while saving record"
                    writer.writerow(row)
                    # FIXME: log it too
            else:
                writer.writerow(row)
