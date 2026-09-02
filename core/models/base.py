from django.db import models

from core.models.managers import AliveManager


class BaseModel(models.Model):
  """
  IMPORTANT:
  For models inheriting BaseModel, _soft_delete_parent_paths,
  _field_requirements, and deleted_at presence are resolved lazily
  from model metadata and then cached per model class
  by the managers/querysets.

  Because of that, these values must stay static for the lifetime of
  the Python process.

  Do not:
  - mutate _soft_delete_parent_paths or _field_requirements at runtime
  - dynamically create or replace model classes in-process
  - write tests that change this model config between tests in one process
  """
  _soft_delete_parent_paths = None
  _field_requirements = None
  _has_deleted_at = False
  _normalized_soft_delete_parent_paths = None
  _normalized_field_requirements = None

  all_objects = models.Manager()
  objects = AliveManager()

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True
    ordering = ['-updated_at']
    base_manager_name = 'all_objects'
    default_manager_name = 'objects'
