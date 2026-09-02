import importlib

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.settings import spectacular_settings


class CustomSchemaGenerator(SchemaGenerator):
  _urls = ''
  _include_urlpattern_names = None
  _tags = []
  _security_schemes = {
    'bearerAuth': {
      'type': 'http',
      'scheme': 'bearer',
      'bearerFormat': 'JWT',
      'description': 'Use `Bearer <access_token>` in the Authorization header.',
    },
    'externalApiKeyAuth': {
      'type': 'apiKey',
      'name': 'X-API-Key',
      'in': 'header',
      'description': 'External API key authentication.'
    },
  }

  def _get_urlpatterns(self):
    mod = importlib.import_module(self._urls)
    return getattr(mod, 'urlpatterns', [])

  def get_schema(self, request=None, public=False):
    spectacular_settings.user_settings['TAGS'] = self._tags

    schema = super().get_schema(request, public)
    if schema:
      schema['components']['securitySchemes'] = self._security_schemes
      schema['tags'] = sorted(schema['tags'], key=lambda tag: tag['name'])

    return schema

  def _get_paths_and_endpoints(self):
    urlpatterns = self._get_urlpatterns()

    if not urlpatterns:
      return []

    if not self._include_urlpattern_names:
      return []

    allowed_callbacks = {
      pattern.callback for pattern in urlpatterns
      if pattern.name in self._include_urlpattern_names
    }

    if not allowed_callbacks:
      return []

    self._initialise_endpoints()

    original_endpoints = self.endpoints
    try:
      self.endpoints = [
        endpoint for endpoint in original_endpoints
        if endpoint[3] in allowed_callbacks
      ]
      return super()._get_paths_and_endpoints()
    finally:
      self.endpoints = original_endpoints
