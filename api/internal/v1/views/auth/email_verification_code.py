from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from api.base.views import BasePublicAPIView
from api.internal.v1.serializers.auth.email import (
  EmailAvailabilitySerializer,
  EmailVerificationCodeEmailSerializer,
  EmailVerificationCodeSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.auth.email_verification import (
  GetEmailAvailabilityDTO,
  GetEmailFromCodeDTO,
  IssueEmailVerificationCodeDTO,
)
from core.services.auth.email_verification import (
  get_email_availability,
  get_email_from_code,
  issue_email_verification_code,
)
from core.services.email.jobs.email_verification import (
  send_email_verification_email,
)


@extend_class_schema
class EmailAvailabilityView(BasePublicAPIView):
  @extend_method_schema(
    resource='email_availability',
    request=EmailAvailabilitySerializer,
    response=EmailAvailabilitySerializer,
    description=(
      'Check the availability of a given email address for '
      'new account sign-up. This API determines if the email has not '
      'been previously registered.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = EmailAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = GetEmailAvailabilityDTO(**serializer.validated_data)
    is_available = get_email_availability(dto=dto)
    return Response({'is_available': is_available}, status=status.HTTP_200_OK)


@extend_class_schema
class EmailVerificationCodeView(BasePublicAPIView):
  @extend_method_schema(
    resource='email_verification_code',
    request=EmailVerificationCodeSerializer,
    response=EmailVerificationCodeSerializer,
    description=(
      'Initiate the account sign-up process by verifying '
      'the provided email address. A successful request triggers '
      'an email to the user with a sign-up link.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = EmailVerificationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email_sent = False
    dto = IssueEmailVerificationCodeDTO(**serializer.validated_data)

    with transaction.atomic():
      code = issue_email_verification_code(dto=dto)
      if code:
        send_email_verification_email(
          email=dto.email,
          verification_code=code.verification_code,
        )
        email_sent = True

    return Response({'email_sent': email_sent}, status=status.HTTP_200_OK)


@extend_class_schema
class EmailVerificationCodeEmailView(BasePublicAPIView):
  @extend_method_schema(
    resource='email_by_email_verification_code',
    request=EmailVerificationCodeEmailSerializer,
    response=EmailVerificationCodeEmailSerializer,
    description=(
      'Fetch email associated with the given verification_code provided '
      'in the sign-up link sent by `email_verification_code` API.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = EmailVerificationCodeEmailSerializer(
      data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = GetEmailFromCodeDTO(**serializer.validated_data)
    email = get_email_from_code(dto=dto)
    return Response({'email': email}, status=status.HTTP_200_OK)
