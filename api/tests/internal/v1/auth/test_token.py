import datetime as dt

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from tests.utils import assertions


@pytest.mark.django_db
class TestTokenPair:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, user_factory):
    self.url = api_reverse('token_pair')
    self.password = 'Pa$$w0rd!'
    self.user = user_factory(password=make_password(self.password))

  def test_login_with_correct_credential(self, login):
    resp = login(email=self.user.email, password=self.password)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assertions.assert_mapping_value_type(
      data=data, key='access', expected_type=str)
    assertions.assert_mapping_value_type(
      data=data, key='refresh', expected_type=str)
    assertions.assert_mapping_numeric_range(
      data=data, key='access_expires_in', expected_type=int, min_value=1)
    assertions.assert_mapping_numeric_range(
      data=data, key='refresh_expires_in', expected_type=int, min_value=1)

    access = AccessToken(data['access'])
    refresh = RefreshToken(data['refresh'])
    assert access['user_id'] == str(self.user.id)
    assert refresh['user_id'] == str(self.user.id)

    exp = dt.datetime.fromtimestamp(access['exp'], tz=dt.timezone.utc)
    assert exp > timezone.now()
    exp = dt.datetime.fromtimestamp(refresh['exp'], tz=dt.timezone.utc)
    assert exp > timezone.now()
    assert data['refresh_expires_in'] > data['access_expires_in']

  def test_invalid_password_cannot_login(self, login):
    resp = login(email=self.user.email, password=f'invalid_{self.password}')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

  def test_invalid_email_cannot_login(self, login):
    resp = login(email=f'invalid_{self.user.email}', password=self.password)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

  def test_sso_email_cannot_login_with_password(
      self, login, sso_email_domain_factory):
    sso_email_domain_factory(email_or_domain=self.user.email)
    resp = login(email=self.user.email, password=self.password)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTokenRefresh:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, token_pair_factory):
    self.url = api_reverse('token_refresh')
    self.expired_access, self.refresh, self.user, *_ = token_pair_factory()

  def test_refresh_access_token(self, anon_client):
    payload = { 'refresh': self.refresh }
    resp = anon_client.post(self.url, payload)
    data = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assertions.assert_mapping_value_type(
      data=data, key='access', expected_type=str)
    assertions.assert_mapping_numeric_range(
      data=data, key='access_expires_in', expected_type=int, min_value=1)

    assert data['access'] != self.expired_access
    access = AccessToken(data['access'])
    assert access['user_id'] == str(self.user.id)

    exp = dt.datetime.fromtimestamp(access['exp'], tz=dt.timezone.utc)
    assert exp > timezone.now()

  def test_invalid_refresh_token_cannot_refresh_access_token(
      self, anon_client):
    payload = { 'refresh': f'{self.refresh}_invalid' }
    resp = anon_client.post(self.url, payload)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRevoke:
  @pytest.fixture(autouse=True)
  def _setup(
      self,
      api_reverse,
      user_factory,
      token_pair_factory,
      api_client_factory,
  ):
    self.url = api_reverse('token_revoke')
    self.user = user_factory(password=make_password('Pa$$w0rd!'))
    self.access, self.refresh, *_ = token_pair_factory(user=self.user)
    self.api_client = api_client_factory(token=self.access)

  def test_revoke_token_pair(self, api_reverse, anon_client):
    payload = { 'refresh': self.refresh }
    resp = self.api_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    url = api_reverse('token_refresh')
    resp = anon_client.post(url, { 'refresh': self.refresh })
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
