import csv

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
        return list(reader)
