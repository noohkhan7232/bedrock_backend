import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password

from core.services.auth.workos import workos_client


logger = logging.getLogger(__name__)

User = get_user_model()


class CustomModelBackend(ModelBackend):
  def authenticate(self, request, email=None, password=None, **kwargs):
    if email is None or password is None:
      return None

    try:
      user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
      # Dummy make_password() must be called here.
      # When the email isn't found, the backend will exist much faster than
      # in the "User exists but the password is wrong" path.
      # Attackers can exploit the gap with a timing attack a.k.a
      # user-enumeration via timing.
      make_password('dummy')
      return None

    if user.check_password(password) and self.user_can_authenticate(user):
      return user
    return None


class SSOBackend(ModelBackend):
  def authenticate(self, request, email=None, code=None, **kwargs):
    if email is None or code is None:
      return None

    try:
      profile_and_token = workos_client.sso.get_profile_and_token(code=code)
    except Exception:
      logger.exception('Unexpected WorkOS SSO error.')
      return None

    if email.strip().lower() != profile_and_token.profile.email.strip().lower():
      make_password('dummy') # timing equaliser
      return None

    try:
      user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
      make_password('dummy') # timing equaliser
      return None

    return user if self.user_can_authenticate(user) else None
