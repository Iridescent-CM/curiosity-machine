import csv
from django.db import transaction, DataError
from django.core.exceptions import ValidationError
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Status(Enum):
    invalid = 0
    saved = 1
    unsaved = 2
    exception = 3

class ResultRow(object):
    """
    Formatter for csv output row
    """
    def __init__(self, status, row, error=None, exception=None):
        reserved_in_use = set(row.keys()).intersection(set(['errors']))
        if reserved_in_use:
            raise Exception('You cannot use these reserved fieldnames in row data: %s' % ", ".join(reserved_in_use))
        self.status = status
        self.data = row
        if error and not isinstance(error, str):
            error = self._format_errors(error)
        self.error = error
        self.exception = exception # FIXME: do something with this

    @staticmethod
    def _format_errors(errors):
        return " ".join(["%s: %s" % (k, " ".join(v)) for k, v in iter(sorted(errors.items()))])

    @property
    def fieldnames(self):
        fieldnames = sorted(list(self.data.keys()))
        fieldnames.extend(["errors"])
        return fieldnames

    @property
    def fields(self):
        fields = self.data.copy()
        if self.error:
            fields.update({'errors': self.error})
        return fields

def decode_lines(f, encoding='utf-8'):
    for line in f:
        yield line.decode(encoding)

class BulkImporter(object):
    """
    Given a ModelForm, BulkImporter will create models from the rows of a CSV data file.

    All rows will be checked for validity first, and no models are created if an invalid
    row is encountered. Exceptions encountered saving a model will be logged but will not
    prevent creation of other models.

    An output CSV will be generated detailing the records created and the errors or exceptions
    encountered. A summary object is also returned detailing the import results.
    """

    def __init__(self, modelformclass, **extra_form_kwargs):
        """
        modelformclass -  the ModelForm to use on input rows
        """
        self.modelformclass = modelformclass
        self.extra_form_kwargs = extra_form_kwargs

    def _open_reader(self, f):
        contents = f.read().decode('utf-8')
        f.seek(0)
        dialect = csv.Sniffer().sniff(contents)
        return csv.DictReader(decode_lines(f))

    def _open_writer(self, f, reader_fieldnames, output_fieldnames):
        reduced_fieldnames = [x for x in reader_fieldnames if x in output_fieldnames]
        extra_fieldnames = [x for x in output_fieldnames if x not in reduced_fieldnames]
        return csv.DictWriter(f, fieldnames=reduced_fieldnames + sorted(extra_fieldnames))

    @staticmethod
    def summarize(status_counts):
        """
        Return the Status to consider the entire file,
        given the statuses of each row
        """

        keys = list(status_counts.keys())
        if keys == [Status.saved]:
            return Status.saved
        elif keys == [Status.unsaved]:
            return Status.unsaved
        elif keys == [Status.invalid]:
            return Status.invalid
        elif set(keys) == set([Status.invalid, Status.unsaved]):
            return Status.invalid
        else:
            return Status.exception

    def call(self, infile, outfile):
        """
        infile  -  A readable binary mode file, assumed to be UTF-8 encoded, containing CSV data with header
        outfile -  A writable text mode file for output
        """
        reader = self._open_reader(infile)

        valids, invalids = [], []
        for row in reader:
            if "errors" in row:
                del row["errors"]

            form = self.modelformclass(row, **self.extra_form_kwargs)

            if form.is_valid():
                valids.append((row, form))
            else:
                invalids.append((row, form))

        try_to_save = not invalids
        results = []

        for row, form in invalids:
            results.append(ResultRow(Status.invalid, row, form.errors))

        for row, form in valids:
            if try_to_save:
                try:
                    with transaction.atomic():
                        # Clean again to check for uniqueness problems with
                        # users already created enforced only through the form
                        form.full_clean()
                        if form.is_valid():
                            obj = form.save()
                            results.append(ResultRow(Status.saved, row))
                        else:
                            results.append(ResultRow(Status.invalid, row, form.errors))
                except Exception as ex:
                    results.append(ResultRow(Status.exception, row, "Exception encountered while saving record", ex))
                    logger.warning("Exception saving row", exc_info=ex)
            else:
                results.append(ResultRow(Status.unsaved, row))

        if results:
            writer = self._open_writer(outfile, reader.fieldnames, results[0].fieldnames)
            writer.writeheader()
            for result_row in results:
                writer.writerow(result_row.fields)

        counts = {}
        for result_row in results:
            counts[result_row.status] = counts.get(result_row.status, 0) + 1

        return {
            "statuses": counts,
            "final": self.summarize(counts)
        }

