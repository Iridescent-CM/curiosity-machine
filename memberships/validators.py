from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.conf import settings
import csv

def member_import_csv_validator(csv_file):
    """
    Validates that CSVs used for member import are small enough to keep
    in memory, and readable as CSVs. Does not validate that members can
    necessarily be created from the data within.
    """

    if csv_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("File is too large (%s)" % filesizeformat(csv_file.size))
    contents = csv_file.read()
    csv_file.seek(0)
    try:
        contents = contents.decode('utf-8')
    except UnicodeDecodeError:
        raise ValidationError("File does not appear to be UTF-8 encoded")
    except:
        raise ValidationError("Unknown error while decoding file")

    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(contents)
    except csv.Error:
        raise ValidationError("Not a valid CSV file")
