import inspect
from collections.abc import Callable

from drf_spectacular.utils import (
  extend_schema,
  extend_schema_field,
  extend_schema_serializer,
  inline_serializer,
  OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes, PYTHON_TYPE_MAPPING
from rest_framework import serializers

from api.paginations import DefaultPageNumberPagination


HTTP_CODE_MAP = {
  'get': 200,
  'post': 201,
  'put': 200,
  'patch': 200,
  'delete': 204,
}

ACTION_MAP = {
  'get': 'retrieve',
  'post': 'create',
  'put': 'update',
  'patch': 'partial_update',
  'delete': 'delete',
}

PAGINATION_PARAMETERS = [
  OpenApiParameter(
    name='page',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Page number, starting from 1.',
  ),
  OpenApiParameter(
    name='page_size',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description=(
      'Number of items per page. Maximum is '
      f'{DefaultPageNumberPagination.max_page_size}.'
    ),
  ),
]

SCHEMA_ATTRS = '_schema_attrs'
SPECTACULAR_ANNOTATION = '_spectacular_annotation'


def extend_method_schema(
  *,
  resource: str | None = None,
  request=None,
  response=None,
  action: str | None = None,
  http_code: int | None = None,
  operation_id: str | None = None,
  description: str | None = None,
  parameters=None,
  query_params=None,
  paginated: bool = False,
  **kwargs,
) -> Callable:
  def decorator(view_method):
    method_name = view_method.__name__.lower()
    status_code = http_code or HTTP_CODE_MAP.get(method_name, 200)

    resolved_request = request
    if method_name in ('get', 'delete'):
      resolved_request = None

    resolved_responses = _get_responses(
      resource=resource,
      method_name=method_name,
      response=response,
      http_code=http_code,
      paginated=paginated,
    )

    resolved_operation_id = operation_id
    if resolved_operation_id is None and resource:
      resolved_action = (
        ACTION_MAP.get(method_name, method_name) if action is None else action
      )
      resolved_operation_id = f'{resolved_action}_{resource}'

    resolved_parameters = list(parameters or [])
    if query_params:
      resolved_parameters += _get_query_parameters(query_params=query_params)
    if paginated:
      resolved_parameters += PAGINATION_PARAMETERS

    extend_schema_kwargs = {
      **kwargs,
      'parameters': resolved_parameters,
      'operation_id': resolved_operation_id,
      'description': description,
      'request': resolved_request,
      'responses': resolved_responses,
    }

    extend_schema_kwargs = {
      key: value for key, value in extend_schema_kwargs.items()
      if value is not None
    }

    annotated_method = extend_schema(**extend_schema_kwargs)(view_method)
    setattr(annotated_method, SCHEMA_ATTRS, extend_schema_kwargs)
    return annotated_method

  return decorator


def make_extend_class_schema(*, api_tags):
  def extend_class_schema(view_class):
    view_class = _annotate_class_tags(view_class=view_class, api_tags=api_tags)
    view_class = _annotate_class_permissions(view_class=view_class)
    return view_class
  return extend_class_schema


def extend_serializer_schema(**kwargs):
  exclude_fields = kwargs.get('exclude_fields', None) or []
  deprecate_fields = kwargs.get('deprecate_fields', None) or []

  def decorator(serializer_class):
    annotation = getattr(serializer_class, SPECTACULAR_ANNOTATION, {}) or {}

    cur_exclude_fields = annotation.get('exclude_fields', None) or []
    cur_deprecate_fields = annotation.get('deprecate_fields', None) or []

    agg_exclude_fields = list(exclude_fields) + list(cur_exclude_fields)
    agg_deprecate_fields = list(deprecate_fields) + list(cur_deprecate_fields)

    resolved_kwargs = dict(kwargs)
    resolved_kwargs['exclude_fields'] = (
      agg_exclude_fields if agg_exclude_fields else None
    )
    resolved_kwargs['deprecate_fields'] = (
      agg_deprecate_fields if agg_deprecate_fields else None
    )

    resolved_kwargs = {
      key: value for key, value in resolved_kwargs.items() if value is not None
    }

    return extend_schema_serializer(**resolved_kwargs)(serializer_class)

  return decorator


def extend_method_field_schema(
  field,
  *,
  many: bool = False,
):
  resolved_field = _resolve_method_field(field=field, many=many)

  def decorator(serializer_method):
    return extend_schema_field(field=resolved_field)(serializer_method)

  return decorator


def _annotate_class_tags(*, view_class, api_tags):
  tags = [
    tag['name'] for tag in api_tags if view_class.__name__ in tag['class_names']
  ]
  return extend_schema(tags=tags)(view_class)


def _annotate_class_permissions(*, view_class):
  for method_name in list(HTTP_CODE_MAP.keys()):
    view_method = getattr(view_class, method_name, None)
    if view_method is None:
      continue

    method_schema_attrs = dict(getattr(view_method, SCHEMA_ATTRS, {}) or {})

    permission_classes = _get_permission_classes(
      view_class=view_class,
      method_name=method_name,
    )

    auth = _get_auth(permission_classes=permission_classes)
    if auth is not None:
      method_schema_attrs['auth'] = auth

    permission_description = _get_permission_description(
      permission_classes=permission_classes,
    )

    method_description = method_schema_attrs.get('description') or ''
    if method_description and permission_description:
      description = f'{method_description}\n\n{permission_description}'
    else:
      description = method_description or permission_description

    if description:
      method_schema_attrs['description'] = description

    if not method_schema_attrs:
      continue

    annotated_method = extend_schema(**method_schema_attrs)(view_method)
    setattr(annotated_method, SCHEMA_ATTRS, method_schema_attrs)
    setattr(view_class, method_name, annotated_method)

  return view_class


def _get_permission_classes(*, view_class, method_name):
  permission_classes = []
  permission_classes += list(getattr(view_class, '_base_permission_classes', []))
  permission_classes += list(getattr(view_class, 'permission_classes', []))
  permission_classes += list(
    getattr(view_class, 'action_permission_classes', {}).get(method_name, [])
  )

  return list(dict.fromkeys(permission_classes))


def _get_permission_description(*, permission_classes):
  descriptions = []

  for permission_class in permission_classes:
    description = getattr(permission_class, 'schema_description', None)
    if description:
      descriptions.append(description)

  if not descriptions:
    return ''

  lines = [f'- {description}' for description in descriptions]
  return '\n'.join(lines)


def _get_auth(*, permission_classes):
  auth = {}

  for permission_class in permission_classes:
    schema_auth = getattr(permission_class, 'schema_auth', None)
    if not schema_auth:
      continue

    auth.update(schema_auth)

  if not auth:
    return None

  return [auth]


def _get_query_parameters(query_params):
  return [
    OpenApiParameter(
      name=name,
      type=PYTHON_TYPE_MAPPING[attrs.get('type', str)],
      location=OpenApiParameter.QUERY,
      required=attrs.get('required', False),
      description=attrs.get('description', ''),
    ) for name, attrs in query_params.items()
  ]


def _is_serializer_class(value):
  return (
    inspect.isclass(value) and issubclass(value, serializers.BaseSerializer)
  )


def _is_many_serializer(value):
  return isinstance(value, serializers.ListSerializer)


def _as_many_schema(value):
  if value is None:
    return None

  if _is_many_serializer(value):
    return value

  if _is_serializer_class(value):
    return value(many=True)

  return value


def _get_paginated_response(
  *,
  resource: str | None,
  responses,
):
  if responses is None:
    return None

  name = (
    f'Paginated{resource.title().replace("_", "")}Response'
    if resource else 'PaginatedResponse'
  )

  return inline_serializer(
    name=name,
    fields={
      'count': serializers.IntegerField(),
      'next': serializers.URLField(allow_null=True),
      'previous': serializers.URLField(allow_null=True),
      'results': _as_many_schema(responses),
    },
  )


def _get_responses(
  *,
  resource: str | None,
  method_name: str,
  response,
  http_code: int | None,
  paginated: bool,
):
  responses = response

  if responses is None:
    return None

  status_code = http_code or HTTP_CODE_MAP.get(method_name, 200)

  if paginated:
    responses = _get_paginated_response(resource=resource, responses=responses)

  return {status_code: responses}


def _resolve_method_field(*, field, many: bool):
  if field in PYTHON_TYPE_MAPPING:
    resolved_field = PYTHON_TYPE_MAPPING[field]

    if many:
      return {
        'type': 'array',
        'items': resolved_field,
      }

    return resolved_field

  if isinstance(field, serializers.BaseSerializer):
    return field

  if (
    inspect.isclass(field)
    and issubclass(field, serializers.BaseSerializer)
  ):
    return field(many=many)

  if isinstance(field, serializers.Field):
    if many:
      return serializers.ListField(child=field)
    return field

  if inspect.isclass(field) and issubclass(field, serializers.Field):
    instance = field()
    if many:
      return serializers.ListField(child=instance)
    return instance

  raise TypeError(
    '_resolve_method_field require a Python type, DRF field, '
    'DRF Field class, Serializer, or Serializer class.'
  )
