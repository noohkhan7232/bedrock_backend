import datetime


def get_never_expire_datetime():
  return datetime.datetime(2999, 12, 31, tzinfo=datetime.timezone.utc)

def get_tenant_image_path(instance, filename):
  from core.models import tenant
  return tenant.get_tenant_image_path(instance, filename)

def get_user_image_path(instance, filename):
  from core.models import user
  return user.get_user_image_path(instance, filename)
