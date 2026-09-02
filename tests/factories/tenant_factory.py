import factory
from django.conf import settings

from core.models import Tenant
from tests.constants import DEFAULTS
from tests.utils.text import generate_random_letters


class TenantFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = Tenant
    django_get_or_create = ('domain',)

  class Params:
    plan = DEFAULTS.PLAN
    enterprise = factory.Trait(plan='enterprise')
    standard = factory.Trait(plan='standard')
    free = factory.Trait(plan='free')

  name = factory.Sequence(lambda n: f'Tenant {n}')
  domain = factory.LazyFunction(
    lambda: generate_random_letters(
      length=settings.TENANT_DOMAIN_LENGTH
    )
  )
  account_id = factory.LazyFunction(
    lambda: generate_random_letters(
      length=settings.TENANT_ACCOUNT_ID_LENGTH
    )
  )
  image = None

  @factory.post_generation
  def seed_defaults(self, create, extracted, **kwargs):
    if not create:
      return

    # If other tenant tables must be set when a new tenant is created,
    # initialize here.
