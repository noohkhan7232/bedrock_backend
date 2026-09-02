from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from api.base.views import BasePublicAPIView
from api.internal.v1.serializers.auth.password_reset_code import (
  PasswordResetCodeEmailSerializer,
  PasswordResetCodeSerializer,
  PasswordResetSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.auth.password_reset import (
  GetEmailFromCodeDTO,
  ResetPasswordDTO,
  SendPasswordResetCodeDTO,
)
from core.services.auth.password_reset import (
  get_email_from_code,
  reset_password,
  send_password_reset_code,
)


@extend_class_schema
class PasswordResetCodeView(BasePublicAPIView):
  @extend_method_schema(
    resource='password_reset_code',
    request=PasswordResetCodeSerializer,
    response=PasswordResetCodeSerializer,
    description=(
      'Initiate the password reset process. '
      'Upon a successful request, an email containing a password reset link '
      'is sent to the specified user\'s email address.'
    ),
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = PasswordResetCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = SendPasswordResetCodeDTO(**serializer.validated_data)
    res = send_password_reset_code(dto=dto)
    return Response(res, status=status.HTTP_200_OK)


@extend_class_schema
class PasswordResetView(BasePublicAPIView):
  @extend_method_schema(
    resource='password_reset',
    request=PasswordResetSerializer,
    response=PasswordResetSerializer,
    description=(
      'Update user\'s password. '
      'It requires authentication using a unique reset code '
      'received via email from the `password_reset_code` API.'
    ),
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = ResetPasswordDTO(**serializer.validated_data)
    res = reset_password(dto=dto)
    return Response(res, status=status.HTTP_200_OK)


@extend_class_schema
class PasswordResetCodeEmailView(BasePublicAPIView):
  @extend_method_schema(
    resource='password_reset_code_email',
    request=PasswordResetCodeEmailSerializer,
    response=PasswordResetCodeEmailSerializer,
    description=(
      'Fetch email associated with the given reset_code provided in '
      'the password reset link sent by `password_reset_code` API.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = PasswordResetCodeEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = GetEmailFromCodeDTO(**serializer.validated_data)
    res = get_email_from_code(dto=dto)
    return Response(res, status=status.HTTP_200_OK)
