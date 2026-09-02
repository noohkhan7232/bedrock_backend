import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
  AuthenticationFailed as DRFAuthenticationFailed,
  NotFound as DRFNotFound,
  PermissionDenied as DRFPermissionDenied,
  ValidationError as DRFValidationError,
  NotAuthenticated as DRFNotAuthenticated,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework_simplejwt.exceptions import (
  InvalidToken as SimpleJWTInvalidToken,
  TokenError as SimpleJWTTokenError,
)

from core.exceptions import (
  AuthenticationFailedError,
  ConflictError,
  DomainValidationError,
  PermissionDeniedError,
  DuplicateRecordError,
  ResourceExpiredError,
  UsageLimitExceededError,
  PayloadTooLargeError,
  ObjectNotFoundError,
  CodeNotFoundError,
  TooManyRequestsError,
  ServiceError,
  EmailServiceError,
  SSOAuthenticationError,
  NoActionTaken,
  JobCancelledError,
)


logger = logging.getLogger(__name__)

EXCEPTION_TO_STATUS_MAP = {
  Http404: status.HTTP_404_NOT_FOUND,
  DjangoPermissionDenied: status.HTTP_403_FORBIDDEN,
  DRFAuthenticationFailed: status.HTTP_401_UNAUTHORIZED,
  DRFNotFound: status.HTTP_404_NOT_FOUND,
  DRFPermissionDenied: status.HTTP_403_FORBIDDEN,
  DRFValidationError: status.HTTP_400_BAD_REQUEST,
  DRFNotAuthenticated: status.HTTP_401_UNAUTHORIZED,
  AuthenticationFailedError: status.HTTP_401_UNAUTHORIZED,
  ConflictError: status.HTTP_409_CONFLICT,
  DomainValidationError: status.HTTP_400_BAD_REQUEST,
  PermissionDeniedError: status.HTTP_403_FORBIDDEN,
  DuplicateRecordError: status.HTTP_409_CONFLICT,
  ResourceExpiredError: status.HTTP_410_GONE,
  UsageLimitExceededError: status.HTTP_422_UNPROCESSABLE_ENTITY,
  PayloadTooLargeError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
  ObjectNotFoundError: status.HTTP_404_NOT_FOUND,
  CodeNotFoundError: status.HTTP_410_GONE,
  TooManyRequestsError: status.HTTP_429_TOO_MANY_REQUESTS,
  ServiceError: status.HTTP_500_INTERNAL_SERVER_ERROR,
  EmailServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
  SSOAuthenticationError: status.HTTP_400_BAD_REQUEST,
  NoActionTaken: status.HTTP_200_OK,
  JobCancelledError: status.HTTP_200_OK,
  SimpleJWTInvalidToken: status.HTTP_401_UNAUTHORIZED,
  SimpleJWTTokenError: status.HTTP_401_UNAUTHORIZED,
}

def _get_status_code(exc):
  for cls in type(exc).mro():
    if cls in EXCEPTION_TO_STATUS_MAP:
      return EXCEPTION_TO_STATUS_MAP[cls]
  return status.HTTP_500_INTERNAL_SERVER_ERROR

def custom_exception_handler(exc, context):
  # exception_handler returns None or Response instance.
  response = drf_exception_handler(exc, context)

  logger.error(f'{type(exc)}: {exc}')

  data = {
    'type': str(type(exc)),
    'action': str(context['view']),
    'messages': [str(exc)],
    'status': _get_status_code(exc),
    'error': True,
  }

  if (response is None) or (not isinstance(response, Response)):
    response = Response(data, status=data['status'])
    logger.error(f'Response data: {response.data}')
    return response

  """The following implementation is assuming that request.data == exc.detail."""
  if isinstance(exc.detail, dict):
    if isinstance(exc, DRFValidationError):
      messages = []
      for key, value in exc.detail.items():
        if key == api_settings.NON_FIELD_ERRORS_KEY:
          messages.append(' '.join(value))
        else:
          messages.append(f'{key}: {" ".join(value)}')
      data['messages'] = messages
    else:
      if 'messages' in exc.detail:
        data['messages'] = exc.detail['messages']
      else:
        messages = []
        for key, value in exc.detail.items():
          messages.append(f'{key}: {" ".join(value)}')
        data['messages'] = messages
  elif isinstance(exc.detail, list):
    data['messages'] = exc.detail
  else:
    data['messages'] = [exc.detail]

  logger.error(f'Response data: {response.data}')
  return Response(data, status=data['status'])
