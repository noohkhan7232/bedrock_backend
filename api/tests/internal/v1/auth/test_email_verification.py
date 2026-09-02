import pytest


@pytest.mark.django_db
class TestEmailVerificationCode:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, user_factory):
    self.url = api_reverse('password_reset_code')

