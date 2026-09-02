import pytest
from django.contrib.auth.hashers import make_password
from rest_framework import status

from core.models import EmailJob, PasswordResetCode
from tests.utils import assertions


@pytest.fixture
def reset_code_factory(api_reverse, user_factory, anon_client):
  def _create():
    url = api_reverse('password_reset_code')
    password = 'Pa$$w0rd!'
    user = user_factory(password=make_password(password))
    payload = { 'email': user.email }
    resp = anon_client.post(url, payload)

    assert resp.status_code == status.HTTP_200_OK
    query = PasswordResetCode.objects.filter(email=user.email)
    assert query.count() == 1
    data = resp.json()
    assert data['email_sent']
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.PASSWORD_RESET,
      to_emails=[user.email],
      tenant_id=None,
      expected_count=1,
    )

    reset_code = query.get().reset_code
    return reset_code, user, password
  return _create

@pytest.mark.django_db
class TestPasswordResetCode:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, user_factory):
    self.url = api_reverse('password_reset_code')
    self.password = 'Pa$$w0rd!'
    self.user = user_factory(password=make_password(self.password))

  def test_request_email_verification_code(self, anon_client):
    payload = { 'email': self.user.email }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    query = PasswordResetCode.objects.filter(email=self.user.email)
    assert query.count() == 1
    data = resp.json()
    assert data['email_sent']
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.PASSWORD_RESET,
      to_emails=[self.user.email],
      tenant_id=None,
      expected_count=1,
    )

  def test_anonymous_cannot_request_password_reset_code(self, anon_client):
    email = f'anon_{self.user.email}'
    payload = { 'email': email }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    query = PasswordResetCode.objects.filter(email=email)
    assert query.count() == 0
    data = resp.json()
    assert not data['email_sent']
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.PASSWORD_RESET,
      to_emails=[self.user.email],
      tenant_id=None,
      expected_count=0,
    )

  def test_sso_email_cannot_request_password_reset_code(
      self, anon_client, sso_email_domain_factory):
    sso_email_domain_factory(email_or_domain=self.user.email)
    payload = { 'email': self.user.email }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    query = PasswordResetCode.objects.filter(email=self.user.email)
    assert query.count() == 0
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.PASSWORD_RESET,
      to_emails=[self.user.email],
      tenant_id=None,
      expected_count=0,
    )


@pytest.mark.django_db
class TestPasswordResetLookupEmail:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, reset_code_factory):
    self.url = api_reverse('password_reset_code_email')
    self.reset_code, self.user, *_ = reset_code_factory()

  def test_get_email_by_password_reset_code(self, anon_client):
    payload = { 'reset_code': self.reset_code }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data['email'] == self.user.email

  def test_invalid_reset_code_cannot_get_email(self, anon_client):
    payload = { 'reset_code': 'invalid_reset_code' }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, reset_code_factory):
    self.url = api_reverse('password_reset')
    self.reset_code, self.user, self.password, *_ = reset_code_factory()
    self.new_password = f'new_{self.password}'

  def test_reset_password(self, anon_client, login):
    payload = {
      'email': self.user.email,
      'reset_code': self.reset_code,
      'password': self.new_password,
    }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data['success']

    resp = login(email=self.user.email, password=self.password)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    resp = login(email=self.user.email, password=self.new_password)
    assert resp.status_code == status.HTTP_200_OK

  def test_invalid_email_cannot_reset_password(self, anon_client, login):
    payload = {
      'email': f'invalid_{self.user.email}',
      'reset_code': self.reset_code,
      'password': self.new_password,
    }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert not data['success']

    resp = login(email=self.user.email, password=self.password)
    assert resp.status_code == status.HTTP_200_OK
    resp = login(email=self.user.email, password=self.new_password)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

  def test_invalids_reset_code_cannot_reset_password(self, anon_client, login):
    payload = {
      'email': self.user.email,
      'reset_code': 'invalid_reset_code',
      'password': self.new_password,
    }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert not data['success']

    resp = login(email=self.user.email, password=self.password)
    assert resp.status_code == status.HTTP_200_OK
    resp = login(email=self.user.email, password=self.new_password)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

  def test_sso_email_cannot_reset_password(
      self, anon_client, sso_email_domain_factory):
    sso_email_domain_factory(email_or_domain=self.user.email)
    payload = {
      'email': self.user.email,
      'reset_code': self.reset_code,
      'password': self.new_password,
    }
    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
