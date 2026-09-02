from rest_framework import serializers


class BaseFromRequestDefault:
  requires_context = True

  def _get_error_meta(self, serializer_field):
    parent = getattr(serializer_field, 'parent', None)
    serializer = getattr(parent, '__class__', None)
    serializer_name = getattr(serializer, '__name__', '<unknown>')
    field_name = getattr(serializer_field, 'field_name', '<unknown>')
    return serializer_name, field_name

  def _get_error_meta_str(self, serializer_field):
    serializer_name, field_name = self._get_error_meta(serializer_field)
    return f'(serializer={serializer_name}, field={field_name})'

  def _get_value_from_request(self, serializer_field, name):
    context = getattr(serializer_field, 'context', {}) or {}
    request = context.get('request')

    if request is None:
      meta = self._get_error_meta_str(serializer_field)
      raise serializers.ValidationError(
        f'`request` is required via context {meta}',
        code='request_required',
      )

    try:
      return getattr(request, name)
    except AttributeError:
      meta = self._get_error_meta_str(serializer_field)
      raise serializers.ValidationError(
        f'`request.{name}` is required {meta}',
        code=f'missing_request_{name}',
      )
