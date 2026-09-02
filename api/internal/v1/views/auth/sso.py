from rest_framework import status
from rest_framework.response import Response

from api.base.views import BasePublicAPIView
from api.internal.v1.serializers.auth.sso import (
  SsoAuthorizationUrlSerializer,
  SsoEnablementStatusSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.auth.sso import (
  GetSsoAuthorizationUrlDTO,
  GetSsoEnabledDTO,
)
from core.services.auth.sso import get_authorization_url, get_sso_enabled


@extend_class_schema
class SsoAuthorizationUrlView(BasePublicAPIView):
  @extend_method_schema(
    resource='sso_authorization_url',
    request=SsoAuthorizationUrlSerializer,
    response=SsoAuthorizationUrlSerializer,
  )
  def post(self, request, *args, **kwargs):
    serializer = SsoAuthorizationUrlSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = GetSsoAuthorizationUrlDTO(**serializer.validated_data)
    authorization_url: str = get_authorization_url(dto=dto)
    return Response(
      {'authorization_url': authorization_url},
      status=status.HTTP_200_OK,
    )


@extend_class_schema
class SsoEnablementStatusView(BasePublicAPIView):
  @extend_method_schema(
    resource='sso_enablement',
    request=SsoEnablementStatusSerializer,
    response=SsoEnablementStatusSerializer,
  )
  def post(self, request, *args, **kwargs):
    serializer = SsoEnablementStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = GetSsoEnabledDTO(**serializer.validated_data)
    sso_enabled = get_sso_enabled(dto=dto)
    message = (
      'The email domain is '
      + ('' if sso_enabled else 'not ')
      + 'managed by SSO.'
    )
    return Response(
      {'sso_enabled': sso_enabled, 'message': message},
      status=status.HTTP_200_OK,
    )
