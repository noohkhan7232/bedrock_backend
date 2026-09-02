from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.user_link import (
  UserLinkSerializer,
  UserLinkUpdateSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.user.link import CreateUserLinkDTO
from core.models import UserLink
from core.services.user.link import create_user_link


@extend_class_schema
class CurrentUserLinkListView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_links',
    response=UserLinkSerializer(many=True),
  )
  def get(self, request, *args, **kwargs):
    query = UserLink.objects.filter(user_id=request.user.id)
    serializer = UserLinkSerializer(query.all(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='user_links',
    request=UserLinkSerializer,
    response=UserLinkSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = UserLinkSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = CreateUserLinkDTO(**serializer.validated_data)
    link = create_user_link(dto=dto)
    serializer = UserLinkSerializer(link)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_class_schema
class CurrentUserLinkView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_link',
    request=UserLinkUpdateSerializer,
    response=UserLinkSerializer,
  )
  def put(self, request, *args, **kwargs):
    link = UserLink.objects.get(
      id=kwargs['user_link_id'],
      user_id=request.user.id,
    )
    serializer = UserLinkUpdateSerializer(link, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    link = serializer.save()
    serializer = UserLinkSerializer(link)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='user_link',
    response=UserLinkSerializer,
  )
  def delete(self, request, *args, **kwargs):
    obj = UserLink.objects.get(
      id=kwargs['user_link_id'],
      user_id=request.user.id,
    )
    serializer = UserLinkSerializer(obj)
    data = serializer.data
    obj.delete()
    return Response(data, status=status.HTTP_200_OK)
