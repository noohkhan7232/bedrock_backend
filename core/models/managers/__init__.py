from functools import lru_cache

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone

from core.utils.email import ensure_valid_email


@lru_cache(maxsize=None)
def get_model_config(model_cls):
  """
  Resolve and validate alive-related model config once per model class.

  This function must only be called after Django model metadata is fully ready.
  """
  field_names = {field.name for field in model_cls._meta.fields}
  has_deleted_at = 'deleted_at' in field_names

  paths = getattr(model_cls, '_soft_delete_parent_paths', None)
  normalized_paths = []
  if paths is not None:
    if not isinstance(paths, (tuple, list)):
      raise TypeError(
        f'{model_cls.__name__}._soft_delete_parent_paths '
        'must be a tuple/list.'
      )

    for path in paths:
      if not isinstance(path, str):
        raise TypeError(
          f'{model_cls.__name__}._soft_delete_parent_paths entries '
          'must be strings.'
        )
      if '__' in path:
        raise ValueError(
          f'{model_cls.__name__}._soft_delete_parent_paths '
          f'entry {path!r} must be a direct path, not a nested lookup.'
        )

      # This is now safe because it runs after app/model loading.
      model_cls._meta.get_field(path)
      normalized_paths.append(path)
  normalized_paths = tuple(normalized_paths)

  requirements = getattr(model_cls, '_field_requirements', None)
  normalized_requirements = {}
  if requirements is not None:
    if not isinstance(requirements, dict):
      raise TypeError(
        f'{model_cls.__name__}._field_requirements must be a dict.'
      )

    for field_name, expected_value in requirements.items():
      if not isinstance(field_name, str):
        raise TypeError(
          f'{model_cls.__name__}._field_requirements keys '
          'must be strings.'
        )
      if '__' in field_name:
        raise ValueError(
          f'{model_cls.__name__}._field_requirements key '
          f'{field_name!r} must be a direct field name, '
          'not a nested lookup.'
        )

      model_cls._meta.get_field(field_name)
      normalized_requirements[field_name] = expected_value

  return {
    'has_deleted_at': has_deleted_at,
    'soft_delete_parent_paths': normalized_paths,
    'field_requirements': normalized_requirements,
  }

class SoftDeleteQuerySet(models.QuerySet):
  def delete(self):
    config = get_model_config(self.model)
    if config['has_deleted_at']:
      return super().update(deleted_at=timezone.now())
    return super().delete()

  def hard_delete(self):
    return super().delete()


class AliveQuerySet(SoftDeleteQuerySet):
  def alive(self):
    """
    Return rows that are not soft-deleted.

    Rules:
    - If the model itself has deleted_at, require deleted_at IS NULL.
    - For each configured parent path, require <path>__deleted_at
      IS NULL.
    - Only direct paths are allowed. Nested lookups are rejected.

    The model may define:
      _soft_delete_parent_paths = ('tenant', 'user', ...)
    """
    config = get_model_config(self.model)

    qs = self
    if config['has_deleted_at']:
      qs = qs.filter(deleted_at__isnull=True)

    for path in config['soft_delete_parent_paths']:
      qs = qs.filter(**{f'{path}__deleted_at__isnull': True})

    return qs


class RequiredFieldsQuerySet(AliveQuerySet):
  def available(self):
    """
    Return rows that are alive() and satisfy configured field
    requirements.

    The model may define:
      _field_requirements = {
        "active": True,
        "status": "active",
      }
    """
    config = get_model_config(self.model)

    qs = self.alive()
    for field_name, expected_value in (
      config['field_requirements'].items()
    ):
      qs = qs.filter(**{field_name: expected_value})

    return qs


class AliveManager(models.Manager.from_queryset(AliveQuerySet)):
  def get_queryset(self):
    return super().get_queryset().alive()


class AvailableManager(
  models.Manager.from_queryset(RequiredFieldsQuerySet)
):
  def get_queryset(self):
    return super().get_queryset().available()


class UserManager(BaseUserManager.from_queryset(AliveQuerySet)):
  """
  This class is implemented by referring to
  django.contrib.auth.models.UserManager (django-3.1.4).
  Majorly fixing part relevant to variable "username".
  """
  use_in_migrations = False

  def get_queryset(self):
    return super().get_queryset().alive()

  def _create_user(self, email, password, **extra_fields):
    email = ensure_valid_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(
      email=email,
      password=password,
      **extra_fields,
    )

  def create_superuser(self, email, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(
      email=email,
      password=password,
      **extra_fields,
    )
