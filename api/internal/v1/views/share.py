from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from core.services.share import get_share


@extend_class_schema
class ShareView(BaseInternalAPIView):
  @extend_method_schema(
    resource='share',
  )
  def get(self, request, *args, **kwargs):
    res = get_share()
    return Response(res, status=status.HTTP_200_OK)
