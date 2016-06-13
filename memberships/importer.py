import csv
from django.db import transaction, DataError

def decode_lines(f, encoding='utf-8'):
    for line in f:
        yield line.decode(encoding)

class Result(object):
    def __init__(self, outfile):
        self.outfile = outfile
        self.writer = None

    def _build_fieldnames(self, keys):
        keys.sort()
        if not "errors" in keys:
            keys.append('errors')
        return keys

    def _format_errors(self, errors):
        return " ".join(["%s: %s" % (k, " ".join(v)) for k, v in iter(sorted(errors.items()))])

    def _init_writer(self, row_keys):
        fieldnames = self._build_fieldnames(row_keys)
        writer = csv.DictWriter(self.outfile, fieldnames=fieldnames)
        writer.writeheader()
        self.writer = writer

    def _write(self, row, errstr=''):
        if "errors" in row.keys():
            raise Exception('errors is a reserved fieldname')

        if not self.writer:
            self._init_writer(list(row.keys()))

        row = row.copy() 
        row.update({
            "errors": errstr
        })
        self.writer.writerow(row)

    def invalid(self, row, errors):
        self._write(row, self._format_errors(errors))

    def saved(self, row):
        self._write(row)

    def save_exception(self, row, exception):
        self._write(row, "Exception encountered while saving record")

    def unsaved(self, row):
        self._write(row)

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

    def call(self, infile, outfile):
        """
        infile  -  A readable binary mode file, assumed to be UTF-8 encoded, containing CSV data with header  
        outfile -  A writable text mode file for output
        """
        reader = self._open_reader(infile)
        result = Result(outfile)

        valid = []
        all_valid = True
        for row in reader:
            if "errors" in row:
                del row["errors"]

            form = self.modelformclass(row)
            if form.is_valid():
                valid.append((row, form))
            else:
                result.invalid(row, form.errors)
                all_valid = False

        for row, form in valid:
            if all_valid:
                try:
                    with transaction.atomic():
                        obj = form.save()
                        result.saved(row)
                except Exception as err:
                    result.save_exception(row, err)
                    # FIXME: log it too
            else:
                result.unsaved(row)
