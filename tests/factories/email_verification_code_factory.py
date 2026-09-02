import factory

from core.models import EmailVerificationCode


class EmailVerificationCodeFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = EmailVerificationCode
    django_get_or_create = ('verification_code',)

  email = factory.Faker('email')

  @classmethod
  def _create(cls, model_class, *args, **kwargs):
    email = kwargs.pop('email')
    obj = model_class(email=email)
    obj.set_verification_code()
    obj.save()
    return obj
