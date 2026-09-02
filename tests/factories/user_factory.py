import factory
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from core.constants import CONSTANTS
from core.models import User, UserEulaAgreement


class UserFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = User
    django_get_or_create = ('email',)

  _HASHED = make_password('Pa$$w0rd!')

  email = factory.Sequence(lambda n: f'user{n}@example.com')
  first_name = 'Test'
  last_name = factory.Sequence(lambda n: f'User{n}')
  password = _HASHED
  locale = 'en'
  timezone_code = 'America/Los_Angeles'

  @factory.post_generation
  def seed_eula_agreement(self, create, extracted, **kwargs):
    if not create:
      return

    UserEulaAgreement.objects.create(
      user=self,
      eula_version=CONSTANTS.USER_EULA_VERSION,
      agreed_at=timezone.now(),
    )


class UserEulaAgreementFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = UserEulaAgreement
    django_get_or_create = ('user',)

  user = factory.SubFactory(UserFactory)
  eula_version = CONSTANTS.USER_EULA_VERSION
  agreed_at = factory.LazyFunction(timezone.now)
