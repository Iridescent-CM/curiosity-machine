import pytest

import csv

def test_foo():
    with open('./example.csv') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            print("XXXXXXXXX", row)

def test_bar():
    with open('./example.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print("YYYYYYYYY", row)