import factory
from django.utils import timezone

from core.models import TenantUser
from tests.factories.tenant_factory import TenantFactory
from tests.factories.user_factory import UserFactory
from tests.constants import DEFAULTS, TENANT_USER_ROLE_MAP


class TenantUserFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = TenantUser
    django_get_or_create = ('tenant', 'user',)

  # Enable to write `TenantUserFactory(role='admin', ...)`
  class Params:
    role = DEFAULTS.TENANT_USER_ROLE
    admin = factory.Trait(role='admin')
    manager = factory.Trait(role='manager')
    member = factory.Trait(role='member')

  # Enable to write `TenantUserFactory(tenant=t1, user=u1, ...)`
  tenant = factory.SubFactory(TenantFactory)
  user = factory.SubFactory(UserFactory)

  title = ''
  description = ''
  disable_email_notification = False
  active = True
  joined_at = factory.LazyFunction(timezone.now)

  @factory.lazy_attribute
  def role_uid(self):
    return TENANT_USER_ROLE_MAP[self.role].uid
