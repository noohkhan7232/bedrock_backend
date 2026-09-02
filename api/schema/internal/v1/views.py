from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from api.schema.constants import (
  INTERNAL_API_DOC_CONTACT,
  INTERNAL_API_DOC_DESCRIPTION,
  INTERNAL_API_DOC_TITLE,
  INTERNAL_API_DOC_TOS,
)
from api.schema.generators import CustomSchemaGenerator
from api.schema.internal.v1.tags import URLPATTERN_NAMES, API_TAGS
from api.schema.utils import get_internal_api_template_name


_VERSION = 'v1'

class _SchemaGenerator(CustomSchemaGenerator):
  _urls = 'api.internal.v1.urls'
  _include_urlpattern_names = URLPATTERN_NAMES
  _tags = API_TAGS


class APIDocView(SpectacularRedocView):
  title = INTERNAL_API_DOC_TITLE
  template_name = get_internal_api_template_name(version=_VERSION)


class APIDownloadView(SpectacularAPIView):
  generator_class = _SchemaGenerator
  custom_settings = {
    'TITLE': INTERNAL_API_DOC_TITLE,
    'VERSION': _VERSION,
    'TOS': INTERNAL_API_DOC_TOS,
    'CONTACT': INTERNAL_API_DOC_CONTACT,
    'DESCRIPTION': INTERNAL_API_DOC_DESCRIPTION,
  }
