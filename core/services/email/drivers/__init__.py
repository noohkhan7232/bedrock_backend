from django.conf import settings

from core.services.email.drivers.base import BaseEmailDriver
from core.services.email.drivers.gmail import GmailDriver
from core.services.email.drivers.smtp import SmtpDriver


EMAIL_DRIVERS = {
  'default': SmtpDriver,
  'gmail': GmailDriver,
  'smtp': SmtpDriver,
}

_email_driver = None

def get_email_driver() -> BaseEmailDriver:
  global _email_driver

  if _email_driver is None:
    _email_driver = EMAIL_DRIVERS[settings.EMAIL_DRIVER]()

  return _email_driver
