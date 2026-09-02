import datetime
import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import get_md5_hash_password

from core.dtos.auth.token import (
  RefreshTokenResultDTO,
  GetTokenPairDTO,
  RefreshTokenDTO,
  RevokeTokenDTO,
  RevokeTokenResultDTO,
  TokenPairDTO,
)
from core.exceptions import (
  AuthenticationFailedError,
  PermissionDeniedError,
  TooManyRequestsError,
)
from core.models import FailedLoginAttempt
from core.services.sso import is_sso_email
from core.utils.clock import get_utc_now

logger = logging.getLogger(__name__)


def _on_login_failed(email: str, ip_address: str | None) -> None:
  if ip_address is None or ip_address == '':
    return

  try:
    FailedLoginAttempt.objects.create(email=email, ip_address=ip_address)
  except Exception:
    logger.exception(
      f'Failed to record failed login attempt'
      f'(email={email}, ip_address={ip_address})'
    )


def _ensure_login_attempts_limit(email: str, ip_address: str | None) -> None:
  if ip_address is None or ip_address == '':
    return

  minutes = settings.LOGIN_LOCK_PERIOD_MINS
  date_to = get_utc_now()
  date_from = date_to - datetime.timedelta(minutes=minutes)

  query = FailedLoginAttempt.objects.filter(
    email__iexact=email,
    ip_address=ip_address,
    attempted_at__range=[date_from, date_to],
  )

  if query.count() >= settings.FAILED_LOGIN_ATTEMPT_MAX_COUNT:
    raise TooManyRequestsError(
      f'Wait {minutes} minutes and try again.'
    )


def _ensure_email_domain(email: str) -> None:
  if is_sso_email(email=email):
    raise PermissionDeniedError('Single Sign-On users can\'t login with password.')


def get_token_pair(dto: GetTokenPairDTO) -> TokenPairDTO:
  _ensure_login_attempts_limit(email=dto.email, ip_address=dto.ip_address)

  try:
    credentials = { 'email': dto.email }
    if dto.sso_code:
      credentials['code'] = dto.sso_code
    else:
      _ensure_email_domain(email=dto.email)
      credentials['password'] = dto.password

    user = authenticate(**credentials)

    if user is None or not api_settings.USER_AUTHENTICATION_RULE(user):
      _on_login_failed(email=dto.email, ip_address=dto.ip_address)
      raise AuthenticationFailedError('No active account')

    refresh = RefreshToken.for_user(user)
    access_expires_in = (
      settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    )
    refresh_expires_in = (
      settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
    )

    token_pair = TokenPairDTO(
      refresh=str(refresh),
      access=str(refresh.access_token),
      refresh_expires_in=int(refresh_expires_in),
      access_expires_in=int(access_expires_in),
    )

    if api_settings.UPDATE_LAST_LOGIN:
      update_last_login(None, user)
  except AuthenticationFailedError:
    logger.exception(
      f'Authentication failed while issuing token pair'
      f'(email={dto.email}, ip_address={dto.ip_address})'
    )
    raise
  except Exception:
    logger.exception(
      f'Unexpected error while issuing token pair'
      f'(email={dto.email}, ip_address={dto.ip_address})'
    )
    raise

  return token_pair


def refresh_token(dto: RefreshTokenDTO) -> RefreshTokenResultDTO:
  try:
    refresh = RefreshToken(dto.refresh)
  except Exception:
    raise AuthenticationFailedError('Refresh token error.')

  User = get_user_model()
  user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)

  if user_id in (None, ''):
    raise AuthenticationFailedError('Refresh token error.')

  try:
    user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
  except User.DoesNotExist:
    raise AuthenticationFailedError('No active account')

  if not api_settings.USER_AUTHENTICATION_RULE(user):
    raise AuthenticationFailedError('No active account')

  if api_settings.CHECK_REVOKE_TOKEN:
    if (
      refresh.payload.get(api_settings.REVOKE_TOKEN_CLAIM)
      != get_md5_hash_password(user.password)
    ):
      if (
        'rest_framework_simplejwt.token_blacklist'
        in settings.INSTALLED_APPS
      ):
        try:
          refresh.blacklist()
        except AttributeError:
          pass
      raise AuthenticationFailedError('Password has changed.')

  access_expires_in = (
    settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
  )
  result = RefreshTokenResultDTO(
    refresh=str(refresh),
    access=str(refresh.access_token),
    access_expires_in=int(access_expires_in),
  )

  if api_settings.ROTATE_REFRESH_TOKENS:
    if api_settings.BLACKLIST_AFTER_ROTATION:
      try:
        refresh.blacklist()
      except AttributeError:
        pass

    refresh.set_jti()
    refresh.set_exp()
    refresh.set_iat()
    refresh.outstand()

    result.refresh = str(refresh)

  return result


def revoke_token(dto: RevokeTokenDTO) -> RevokeTokenResultDTO:
  message = 'Token revoked successfully.'

  try:
    token = RefreshToken(dto.refresh)
    token.blacklist()
  except Exception:
    message = 'Invalid refresh token provided.'

  return RevokeTokenResultDTO(message=message)
