from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.base.views import BaseInternalAPIView, BasePublicAPIView
from api.internal.v1.serializers.common import (
  ReadOnlyTenantMinSerializer,
)
from api.internal.v1.serializers.tenant_invitation_code import (
  CurrentUserTenantInvitationCodeSerializer,
  TenantInvitationCodeDetailSerializer,
  TenantInvitationCodeEmailSerializer,
  TenantInvitationCodeListSerializer,
  TenantInvitationCodeSerializer,
  TenantInvitationCodeTenantSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import IsTenantAdmin
from core.dtos.tenant_invitation import (
  AcceptTenantInvitationDTO,
  DeclineTenantInvitationDTO,
  GetEmailFromCodeDTO,
  GetTenantFromCodeDTO,
  InviteToTenantDTO,
)
from core.services.tenant_invitation import (
  accept_invitation,
  decline_invitation,
  delete_tenant_invitation_codes,
  invite_to_tenant,
  get_email_from_code,
  get_tenant_from_code,
)
from core.services.tenant_invitation.querysets import (
  get_tenant_invitation_codes,
  get_current_user_tenant_invitation_codes,
)
from core.services.email.jobs.tenant_invitation import send_invitation_email
from core.utils.query import get_query_param


@extend_class_schema
class TenantInvitationCodeListView(BaseInternalAPIView):
  permission_classes = (IsTenantAdmin,)

  @extend_method_schema(
    resource='tenant_invitation_codes',
    response=TenantInvitationCodeSerializer(many=True),
    description=(
      'Fetch the history of all invitations sent within a tenant.'
    ),
    query_params={
      'search': {
        'type': str,
        'description': 'When provided, records matching the string will be returned.'
      },
    },
    paginated=True,
  )
  def get(self, request, *args, **kwargs):
    search = get_query_param(request=request, key='search', cast=str)
    query = get_tenant_invitation_codes(
      tenant_id=request.tenant.id,
      search=search,
    )

    paginator = api_settings.DEFAULT_PAGINATION_CLASS()
    page = paginator.paginate_queryset(query, request, view=self)
    serializer = TenantInvitationCodeSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)

  @extend_method_schema(
    resource='tenant_invitation_codes',
    request=TenantInvitationCodeListSerializer(many=True),
    response=TenantInvitationCodeListSerializer(many=True),
    description=(
      'Invite existing or new users to join the tenant. '
      'Successful requests trigger an email with a tenant-joining link '
      'to the invited users.'
    ),
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = TenantInvitationCodeListSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = InviteToTenantDTO(**serializer.validated_data)
    tenant_invitation_codes = invite_to_tenant(dto=dto)

    for obj in tenant_invitation_codes:
      send_invitation_email(
        tenant_id=obj.tenant_id,
        user_id=request.user.id,
        email=obj.email,
        invitation_code=obj.invitation_code,
      )

    serializer = TenantInvitationCodeSerializer(
      tenant_invitation_codes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class TenantInvitationCodeView(BaseInternalAPIView):
  permission_classes = (IsTenantAdmin,)

  @extend_method_schema(
    resource='tenant_invitation_code',
    response=TenantInvitationCodeSerializer,
    description=(
      'Delete a specific tenant invitation code. After deletion, the code '
      'becomes invalid, preventing its use for joining the tenant.'
    ),
  )
  def delete(self, request, *args, **kwargs):
    delete_tenant_invitation_codes(
      tenant_id=request.tenant.id,
      tenant_invitation_code_id=kwargs['tenant_invitation_code_id'],
    )
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_class_schema
class TenantInvitationCodeEmailView(BasePublicAPIView):
  @extend_method_schema(
    resource='email_by_tenant_invitation_code',
    request=TenantInvitationCodeEmailSerializer,
    response=TenantInvitationCodeEmailSerializer,
    description=(
      'Fetch email associated with the given invitation_code '
      'provided in the tenant-joining link sent by '
      '`tenant_invitation_codes` API.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = TenantInvitationCodeEmailSerializer(
      data=request.data,
    )
    serializer.is_valid(raise_exception=True)
    dto = GetEmailFromCodeDTO(**serializer.validated_data)
    email = get_email_from_code(dto=dto)
    return Response(
      {'email': email, 'message': ''},
      status=status.HTTP_200_OK,
    )


@extend_class_schema
class TenantInvitationCodeTenantView(BasePublicAPIView):
  @extend_method_schema(
    resource='tenant_by_tenant_invitation_code',
    request=TenantInvitationCodeTenantSerializer,
    response=ReadOnlyTenantMinSerializer,
    description=(
      'Fetch tenant associated with the given invitation_code '
      'provided in the tenant-joining link sent by '
      '`tenant_invitation_codes` API.'
    ),
  )
  def post(self, request, *args, **kwargs):
    serializer = TenantInvitationCodeTenantSerializer(
      data=request.data,
    )
    serializer.is_valid(raise_exception=True)
    dto = GetTenantFromCodeDTO(**serializer.validated_data)
    tenant = get_tenant_from_code(dto=dto)

    serializer = ReadOnlyTenantMinSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class CurrentUserTenantInvitationCodeAcceptView(BaseInternalAPIView):
  @extend_method_schema(
    resource='accept_tenant_invitation_code',
    request=CurrentUserTenantInvitationCodeSerializer,
    response=ReadOnlyTenantMinSerializer,
  )
  def post(self, request, *args, **kwargs):
    serializer = (
      CurrentUserTenantInvitationCodeSerializer(
        data=request.data,
        context={'request': request},
      )
    )
    serializer.is_valid(raise_exception=True)
    dto = AcceptTenantInvitationDTO(**serializer.validated_data)
    tenant = accept_invitation(dto=dto)
    serializer = ReadOnlyTenantMinSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_class_schema
class CurrentUserTenantInvitationCodeDeclineView(BaseInternalAPIView):
  @extend_method_schema(
    resource='decline_tenant_invitation_code',
    request=CurrentUserTenantInvitationCodeSerializer,
    response=ReadOnlyTenantMinSerializer,
  )
  def post(self, request, *args, **kwargs):
    serializer = (
      CurrentUserTenantInvitationCodeSerializer(
        data=request.data,
        context={'request': request},
      )
    )
    serializer.is_valid(raise_exception=True)
    dto = DeclineTenantInvitationDTO(**serializer.validated_data)
    tenant = decline_invitation(dto=dto)
    serializer = ReadOnlyTenantMinSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class CurrentUserTenantInvitationCodeListView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_tenant_invitation_codes',
    response=TenantInvitationCodeDetailSerializer,
    paginated=True,
  )
  def get(self, request, *args, **kwargs):
    query = get_current_user_tenant_invitation_codes(email=request.user.email)

    paginator = api_settings.DEFAULT_PAGINATION_CLASS()
    page = paginator.paginate_queryset(query, request, view=self)
    serializer = TenantInvitationCodeDetailSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)
