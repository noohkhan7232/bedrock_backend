from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.user_language import (
  UserLanguageSerializer,
  UserLanguageUpdateSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.user.language import CreateUserLanguageDTO
from core.models import UserLanguage
from core.services.user.language import create_user_language


@extend_class_schema
class CurrentUserLanguageListView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_languages',
    request=UserLanguageSerializer,
    response=UserLanguageSerializer,
  )
  def post(self, request, *args, **kwargs):
    serializer = UserLanguageSerializer(
      data=request.data,
      context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    dto = CreateUserLanguageDTO(**serializer.validated_data)
    lang = create_user_language(dto=dto)
    serializer = UserLanguageSerializer(lang)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_class_schema
class CurrentUserLanguageView(BaseInternalAPIView):
  @extend_method_schema(
    resource='user_language',
    request=UserLanguageUpdateSerializer,
    response=UserLanguageSerializer,
  )
  def put(self, request, *args, **kwargs):
    lang = UserLanguage.objects.get(
      id=kwargs['user_language_id'],
      user_id=request.user.id,
    )
    serializer = UserLanguageUpdateSerializer(
      lang,
      data=request.data,
      partial=True,
    )
    serializer.is_valid(raise_exception=True)
    lang = serializer.save()
    serializer = UserLanguageSerializer(lang)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @extend_method_schema(
    resource='user_language',
    response=UserLanguageSerializer,
  )
  def delete(self, request, *args, **kwargs):
    obj = UserLanguage.objects.get(
      id=kwargs['user_language_id'],
      user_id=request.user.id,
    )
    serializer = UserLanguageSerializer(obj)
    data = serializer.data
    obj.delete()
    return Response(data, status=status.HTTP_200_OK)
