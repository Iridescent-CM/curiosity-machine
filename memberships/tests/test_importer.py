import pytest

from io import BytesIO

from memberships.admin.importer import Importer

@pytest.mark.xfail
def test_importer_parses_csv_into_dicts():
    importer = Importer()
    input = BytesIO(b"a,b,c\n1,2,3\n4,5,6")
    assert importer.parse(input) == [
        {"a":"1", "b":"2", "c":"3"}, 
        {"a":"4", "b":"5", "c":"6"}, 
    ]
