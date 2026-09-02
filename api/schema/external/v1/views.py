from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from api.schema.constants import (
  EXTERNAL_API_DOC_CONTACT,
  EXTERNAL_API_DOC_DESCRIPTION,
  EXTERNAL_API_DOC_TITLE,
  EXTERNAL_API_DOC_TOS,
)
from api.schema.generators import CustomSchemaGenerator
from api.schema.external.v1.tags import URLPATTERN_NAMES, API_TAGS
from api.schema.utils import get_external_api_template_name


_VERSION = 'v1'

class _SchemaGenerator(CustomSchemaGenerator):
  _urls = 'api.external.v1.urls'
  _include_urlpattern_names = URLPATTERN_NAMES
  _tags = API_TAGS


class APIDocView(SpectacularRedocView):
  title = EXTERNAL_API_DOC_TITLE
  template_name = get_external_api_template_name(version=_VERSION)


class APIDownloadView(SpectacularAPIView):
  generator_class = _SchemaGenerator
  redoc_url_params = {
    'redoc_title': 'Test',
  }
  custom_settings = {
    'TITLE': EXTERNAL_API_DOC_TITLE,
    'VERSION': _VERSION,
    'TOS': EXTERNAL_API_DOC_TOS,
    'CONTACT': EXTERNAL_API_DOC_CONTACT,
    'DESCRIPTION': EXTERNAL_API_DOC_DESCRIPTION,
  }
