from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.common import (
  ReadOnlyTenantSerializer,
)
from api.internal.v1.serializers.tenant import (
  NewTenantSerializer,
  ReadOnlyTenantDetailSerializer,
  TenantDeleteSerializer,
  TenantUpdateSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import IsTenantAdmin, IsTenantMember
from core.dtos.tenant import CreateTenantDTO, DeleteTenantDTO
from core.models import Tenant
from core.services.tenant import create_tenant, delete_tenant


@extend_class_schema
class NewTenantView(BaseInternalAPIView):
  @extend_method_schema(
    resource='new_tenant',
    request=NewTenantSerializer,
    response=ReadOnlyTenantDetailSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = NewTenantSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = CreateTenantDTO(**serializer.validated_data)
    tenant = create_tenant(dto=dto)

    serializer = ReadOnlyTenantDetailSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_class_schema
class TenantView(BaseInternalAPIView):
  action_permission_classes = {
    'get': (IsTenantMember,),
    'post': (IsTenantAdmin,),
    'delete': (IsTenantAdmin,),
  }

  @extend_method_schema(
    resource='tenant',
    response=ReadOnlyTenantDetailSerializer,
  )
  def get(self, request, *args, **kwargs):
    tenant = request.tenant
    serializer = ReadOnlyTenantDetailSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='tenant',
    request=TenantUpdateSerializer,
    response=ReadOnlyTenantSerializer,
  )
  def put(self, request, *args, **kwargs):
    tenant = request.tenant
    serializer = TenantUpdateSerializer(tenant, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    tenant = serializer.save()
    serializer = ReadOnlyTenantSerializer(tenant)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='tenant',
  )
  @transaction.atomic
  def delete(self, request, *args, **kwargs):
    serializer = TenantDeleteSerializer(data={}, context={'request': request})
    serializer.is_valid(raise_exception=True)
    dto = DeleteTenantDTO(**serializer.validated_data)
    delete_tenant(dto=dto)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_class_schema
class CurrentUserTenantListView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_tenants',
    response=ReadOnlyTenantDetailSerializer(many=True),
  )
  def get(self, request, *args, **kwargs):
    query = (
      Tenant.objects
        .filter(
          tenantuser__user_id=request.user.id,
          tenantuser__active=True,
          tenantuser__deleted_at__isnull=True,
          tenantuser__user__deleted_at__isnull=True,
          deleted_at__isnull=True,
        )
        .distinct()
    )

    paginator = api_settings.DEFAULT_PAGINATION_CLASS()
    page = paginator.paginate_queryset(query, request, view=self)
    serializer = ReadOnlyTenantDetailSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)
