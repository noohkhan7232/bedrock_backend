from typing import Literal, Sequence

from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.views import APIView

from api.permissions import IsAuthenticated, HasValidExternalAPIKey

HTTPMethod = Literal['get', 'post', 'put', 'patch', 'delete']


class BaseAPIView(APIView):
  """
  `_base_permission_classes` and `permission_classes` are
  applied to all HTTP methods.
  `action_permission_classes` are appended per HTTP method, not replaced.
  Check order: `_base_permission_classes`, then `permission_classes`,
  then `action_permission_classes`.
  """
  _base_permission_classes: list[type[BasePermission]] = []
  permission_classes: list[type[BasePermission]] = []
  action_permission_classes: dict[HTTPMethod, list[type[BasePermission]]] = {}

  def _dedupe_permissions(
    self,
    permissions: Sequence[type[BasePermission]],
  ) -> list[type[BasePermission]]:
    return list(dict.fromkeys(permissions))

  def get_permissions(self) -> list[BasePermission]:
    method = self.request.method.lower()
    merged_permissions = list(self._base_permission_classes or [])
    merged_permissions += list(self.permission_classes or [])
    merged_permissions += list(self.action_permission_classes.get(method, []))
    deduped_permissions = self._dedupe_permissions(merged_permissions)

    return [permission() for permission in deduped_permissions]


class BasePublicAPIView(BaseAPIView):
  _base_permission_classes: list[type[BasePermission]] = [AllowAny]


class BaseInternalAPIView(BaseAPIView):
  _base_permission_classes: list[type[BasePermission]] = [IsAuthenticated]


class BaseExternalAPIView(BaseAPIView):
  _base_permission_classes: list[type[BasePermission]] = [HasValidExternalAPIKey]
