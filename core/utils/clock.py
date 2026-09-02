import datetime
from dateutil.relativedelta import relativedelta

from core.exceptions import ResourceExpiredError


def get_utc_now():
  return datetime.datetime.now(datetime.timezone.utc)


def is_expired(
    obj, key=None, days_margin=0, months_margin=0, years_margin=0,
    raise_exception=False):
  date = getattr(obj, key) if key else obj
  margin = relativedelta(days=days_margin, months=months_margin, years=years_margin)

  is_expired = get_utc_now() > date + margin

  if is_expired and raise_exception:
    raise ResourceExpiredError('The link/code has expired.')

  return is_expired
