import pytest
from django.db import connection


@pytest.mark.django_db
def test_pytest_is_configured():
  with connection.cursor() as cur:
    cur.execute('SELECT 1')
    assert cur.fetchone()[0] == 1
  assert 1 == 1

