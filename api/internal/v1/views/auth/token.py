from ipware import get_client_ip
from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView, BasePublicAPIView
from api.internal.v1.serializers.auth.token import (
  TokenPairSerializer,
  TokenRefreshSerializer,
  TokenRevokeSerializer,
)
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.dtos.auth.token import (
  GetTokenPairDTO,
  RefreshTokenDTO,
  RevokeTokenDTO,
)
from core.services.auth.token import (
  get_token_pair,
  refresh_token,
  revoke_token,
)


@extend_class_schema
class TokenPairView(BasePublicAPIView):
  @extend_method_schema(
    resource='token',
    request=TokenPairSerializer,
    response=TokenPairSerializer,
    description='Retrieve access token and refresh token.'
  )
  def post(self, request, *args, **kwargs):
    ip_address, is_routable = get_client_ip(request)

    serializer = TokenPairSerializer(
      data=request.data,
      context={ 'ip_address': ip_address },
    )
    serializer.is_valid(raise_exception=True)
    dto = GetTokenPairDTO(**serializer.validated_data)
    token_pair = get_token_pair(dto=dto)

    return Response(token_pair.model_dump(), status=status.HTTP_200_OK)


@extend_class_schema
class TokenRefreshView(BasePublicAPIView):
  @extend_method_schema(
    resource='token_refresh',
    request=TokenRefreshSerializer,
    response=TokenRefreshSerializer,
    description='Refresh access token.',
  )
  def post(self, request, *args, **kwargs):
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = RefreshTokenDTO(**serializer.validated_data)
    result = refresh_token(dto=dto)
    return Response(result.model_dump(), status=status.HTTP_200_OK)


@extend_class_schema
class TokenRevokeView(BaseInternalAPIView):
  @extend_method_schema(
    resource='token_revoke',
    request=TokenRevokeSerializer,
    response=TokenRevokeSerializer,
    description='Revoke access token and refresh token.',
  )
  def post(self, request, *args, **kwargs):
    serializer = TokenRevokeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dto = RevokeTokenDTO(**serializer.validated_data)
    result = revoke_token(dto=dto)
    return Response(result.model_dump(), status=status.HTTP_200_OK)
