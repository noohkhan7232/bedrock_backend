from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.common import (
  ReadOnlyTenantUserMinSerializer,
  ReadOnlyTenantUserSerializer,
)
from api.internal.v1.serializers.tenant_user import (
  CurrentTenantUserDeleteSerializer,
  CurrentTenantUserUpdateSerializer,
  MatchedTenantUserSerializer,
  TenantUserDeleteSerializer,
  TenantUserRoleUpdateSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import (
  IsTenantAdmin,
  IsTenantMember,
)
from core.dtos.tenant_user import (
  DeleteCurrentTenantUserDTO,
  DeleteTenantUserDTO,
  UpdateTenantUserRoleDTO,
)
from core.models import TenantUser
from core.services.tenant_user import (
  delete_current_tenant_user,
  delete_tenant_user,
  update_tenant_user_role,
)
from core.services.tenant_user.querysets import (
  get_tenant_users,
  get_matched_tenant_users,
)
from core.utils.query import get_query_param


@extend_class_schema
class TenantUserListView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='tenant_users',
    response=ReadOnlyTenantUserSerializer,
    query_params={
      'search': {
        'type': str,
        'description': 'When provided, users matching the string will be returned.',
      },
      'role': {
        'type': int,
        'description': 'When provided, tenant users whose roles matching the given role will be returned',
      },
    },
    paginated=True,
  )
  def get(self, request, *args, **kwargs):
    role_uid = get_query_param(request=request, key='role', cast=int)
    search = get_query_param(request=request, key='search', cast=str)

    query = get_tenant_users(
      tenant_id=request.tenant.id,
      role_uid=role_uid,
      search=search,
    )

    paginator = api_settings.DEFAULT_PAGINATION_CLASS()
    page = paginator.paginate_queryset(query, request, view=self)
    serializer = ReadOnlyTenantUserSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@extend_class_schema
class TenantUserView(BaseInternalAPIView):
  action_permission_classes = {
    'get': (IsTenantMember,),
    'delete': (IsTenantAdmin,),
  }

  @extend_method_schema(
    resource='tenant_user',
    response=ReadOnlyTenantUserSerializer,
  )
  def get(self, request, *args, **kwargs):
    obj = TenantUser.available.get(id=kwargs['tenant_user_id'])
    serializer = ReadOnlyTenantUserSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='tenant_user',
    response=ReadOnlyTenantUserSerializer,
  )
  def delete(self, request, *args, **kwargs):
    serializer = TenantUserDeleteSerializer(
      data={},
      context={
        'request': request,
        'target_tenant_user_id': kwargs['tenant_user_id'],
      },
    )
    serializer.is_valid(raise_exception=True)
    dto = DeleteTenantUserDTO(**serializer.validated_data)
    delete_tenant_user(dto=dto)

    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_class_schema
class CurrentTenantUserView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='current_tenant_user',
    response=ReadOnlyTenantUserSerializer,
    description=(
      'Fetch data about the tenant user linked to the account '
      'specified by the request\'s token, within the context of '
      'the current tenant.'
    ),
  )
  def get(self, request, *args, **kwargs):
    tenant_user = request.tenant_user
    serializer = ReadOnlyTenantUserSerializer(tenant_user)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='current_tenant_user',
    request=CurrentTenantUserUpdateSerializer,
    response=ReadOnlyTenantUserMinSerializer,
  )
  def put(self, request, *args, **kwargs):
    tenant_user = request.tenant_user
    serializer = CurrentTenantUserUpdateSerializer(
      tenant_user,
      data=request.data,
      partial=True,
    )
    serializer.is_valid(raise_exception=True)
    tenant_user = serializer.save()
    serializer = ReadOnlyTenantUserMinSerializer(tenant_user)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='current_tenant_user',
    request=CurrentTenantUserDeleteSerializer,
    description=(
      'This API can be exeucted if the tenant user is an admin '
      'and there are other tenant admins in the workspace.'
    ),
  )
  def delete(self, request, *args, **kwargs):
    serializer = CurrentTenantUserDeleteSerializer(
      data={},
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = DeleteCurrentTenantUserDTO(**serializer.validated_data)
    delete_current_tenant_user(dto=dto)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_class_schema
class TenantUserRoleView(BaseInternalAPIView):
  permission_classes = (IsTenantAdmin,)

  @extend_method_schema(
    resource='tenant_user_role',
    request=TenantUserRoleUpdateSerializer,
    response=ReadOnlyTenantUserMinSerializer,
  )
  def put(self, request, *args, **kwargs):
    serializer = TenantUserRoleUpdateSerializer(
      data=request.data,
      context={
        'request': request,
        'target_tenant_user_id': kwargs['tenant_user_id'],
      },
    )
    serializer.is_valid(raise_exception=True)
    dto = UpdateTenantUserRoleDTO(**serializer.validated_data)
    target_tenant_user = update_tenant_user_role(dto=dto)

    serializer = ReadOnlyTenantUserMinSerializer(target_tenant_user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class TenantUserAutocompleteView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='tenant_user_autocomplete',
    response=MatchedTenantUserSerializer(many=True),
    query_params={
      'search': {
        'type': str,
        'description': 'When provided, users matching the string will be returned.',
      },
      'include_self': {
        'type': bool,
        'description': 'When provided, current user could be contained in the result.'
      },
      'limit': {
        'type': int,
        'description': 'When provided, this number of results will be returned.'
      },
    },
  )
  def get(self, request, *args, **kwargs):
    search = get_query_param(request=request, key='search', cast=str)
    include_self = get_query_param(
      request=request,
      key='include_self',
      cast=bool,
    )
    limit = get_query_param(request=request, key='limit', cast=int)

    query = get_matched_tenant_users(
      actor_tenant_user_id=request.tenant_user.id,
      search=search,
      include_self=include_self,
      limit=limit,
    )

    serializer = MatchedTenantUserSerializer(query, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
