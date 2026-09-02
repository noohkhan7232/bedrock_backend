from core.constants import PLANS, TENANT_USER_ROLES


class UserRequiredContext:
  default_context = {
    'authorized': False,
    'in_tenant': False,
    'role_uid': TENANT_USER_ROLES.MEMBER.uid,
    'plan': PLANS.FREE,
    'is_resource_owner': False,
  }

  @classmethod
  def get_default_context(cls):
    return {
      'authorized': False,
      'in_tenant': False,
      'role_uid': TENANT_USER_ROLES.MEMBER.uid,
      'plan': PLANS.FREE,
      'is_resource_owner': False,
    }

  @classmethod
  def get_attr_name(cls):
    return '_user_required_context'

  @classmethod
  def overwrite_user_context(cls, func, key, value, attr_name):
    attr_name = attr_name if attr_name else cls.get_attr_name()
    user_context = getattr(func, attr_name, cls.get_default_context())
    user_context[key] = value
    setattr(func, attr_name, user_context)

  @classmethod
  def authorized(cls, func, attr_name=None):
    cls.overwrite_user_context(
      func=func, key='authorized', value=True, attr_name=attr_name)

  @classmethod
  def in_tenant(cls, func, attr_name=None):
    cls.authorized(func, attr_name=attr_name)
    cls.overwrite_user_context(
      func=func, key='in_tenant', value=True, attr_name=attr_name)

  @classmethod
  def is_manager(cls, func, attr_name=None):
    cls.authorized(func, attr_name=attr_name)
    cls.in_tenant(func, attr_name=attr_name)

    cls.overwrite_user_context(
      func=func,
      key='role_uid',
      value=TENANT_USER_ROLES.MANAGER.uid,
      attr_name=attr_name)

  @classmethod
  def is_admin(cls, func, attr_name=None):
    cls.authorized(func, attr_name=attr_name)
    cls.in_tenant(func, attr_name=attr_name)

    cls.overwrite_user_context(
      func=func,
      key='role_uid',
      value=TENANT_USER_ROLES.ADMIN.uid,
      attr_name=attr_name)

  @classmethod
  def is_enterprise(cls, func, attr_name=None):
    cls.authorized(func, attr_name=attr_name)
    cls.in_tenant(func, attr_name=attr_name)

    cls.overwrite_user_context(
      func=func,
      key='plan',
      value=PLANS.ENTERPRISE,
      attr_name=attr_name)
