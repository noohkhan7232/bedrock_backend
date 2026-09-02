from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from api.base.views import BasePublicAPIView, BaseInternalAPIView
from api.internal.v1.serializers.common import (
  ReadOnlyUserSerializer,
)
from api.internal.v1.serializers.user import (
  CurrentUserDeleteSerializer,
  CurrentUserEmailSerializer,
  CurrentUserImageUpdateSerializer,
  CurrentUserPasswordSerializer,
  CurrentUserSerializer,
  NewUserSerializer,
  CurrentUserUpdateSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.constants import TENANT_USER_ROLES
from core.dtos.user import (
  CreateUserDTO,
  DeleteCurrentUserDTO,
  UpdateUserImageDTO,
  UpdateUserPasswordDTO,
)
from core.dtos.tenant_user import CreateInvitedTenantUserDTO
from core.models import User
from core.services.email.jobs.signup_welcome import (
  send_signup_welcome_email,
)
from core.services.tenant_user import create_invited_tenant_user
from core.services.user import (
  create_user,
  delete_current_user,
  update_user_image,
  update_user_password,
)


@extend_class_schema
class CurrentUserView(BaseInternalAPIView):
  @extend_method_schema(
    resource='current_user',
    response=CurrentUserSerializer,
    description=(
      'Fetch data about the user that is currently authenticated '
      'and making the request.'
    ),
  )
  def get(self, request, *args, **kwargs):
    obj = User.objects.get(pk=request.user.id)
    serializer = CurrentUserSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='current_user',
    request=CurrentUserUpdateSerializer,
    response=ReadOnlyUserSerializer,
    description=(
      'Update data about the user that is currently authenticated '
      'and making the request.'),
  )
  def put(self, request, *args, **kwargs):
    user = request.user
    serializer = CurrentUserUpdateSerializer(
      user,
      data=request.data,
      partial=True,
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    serializer = ReadOnlyUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='current_user_delete',
    request=CurrentUserDeleteSerializer,
    description=(
      'If user is only admin of any tenants which have '
      'other non-admin tenant users, this API returns error.'
    ),
  )
  def delete(self, request, *args, **kwargs):
    serializer = CurrentUserDeleteSerializer(
      data={},
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = DeleteCurrentUserDTO(**serializer.validated_data)
    delete_current_user(dto=dto)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_class_schema
class CurrentUserEmailView(BaseInternalAPIView):
  @extend_method_schema(
    resource='current_user_email',
    response=CurrentUserEmailSerializer,
    description=(
      'Fetch email about the user that is currently authenticated '
      'and making the request.'
    ),
  )
  def get(self, request, *args, **kwargs):
    obj = User.objects.get(pk=request.user.id)
    serializer = CurrentUserEmailSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class CurrentUserImageView(BaseInternalAPIView):
  @extend_method_schema(
    resource='current_user_image',
    request=CurrentUserImageUpdateSerializer,
    response=ReadOnlyUserSerializer,
    description=(
      'Update image of the user that is currently authenticated '
      'and making the request.'),
  )
  def put(self, request, *args, **kwargs):
    serializer = CurrentUserImageUpdateSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = UpdateUserImageDTO(**serializer.validated_data)
    user = update_user_image(dto=dto)
    serializer = ReadOnlyUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class CurrentUserPasswordView(BaseInternalAPIView):
  @extend_method_schema(
    resource='current_user_password',
    request=CurrentUserPasswordSerializer,
    description=(
      'Update password of the user that is currently authenticated '
      'and making the request.'),
  )
  def post(self, request, *args, **kwargs):
    serializer = CurrentUserPasswordSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = UpdateUserPasswordDTO(**serializer.validated_data)
    update_user_password(dto=dto)
    return Response({}, status=status.HTTP_200_OK)


@extend_class_schema
class NewUserView(BasePublicAPIView):
  @extend_method_schema(
    resource='new_user',
    request=NewUserSerializer,
    response=NewUserSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = NewUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    dto = CreateUserDTO(**serializer.validated_data)
    user, token_pair = create_user(dto=dto)

    invitation_code = request.data.get('invitation_code', '')
    tenant_id = None
    if invitation_code:
      dto_tenant_user = CreateInvitedTenantUserDTO(
        email=user.email,
        invitation_code=invitation_code,
        role_uid=TENANT_USER_ROLES.MEMBER.uid,
      )
      tenant_user = create_invited_tenant_user(dto=dto_tenant_user)
      tenant_id = tenant_user.tenant.id

    send_signup_welcome_email(email=user.email, tenant_id=tenant_id)

    return Response(
      dict(token_pair=token_pair),
      status=status.HTTP_201_CREATED,
    )
