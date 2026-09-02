import pytest
from rest_framework import status

from core.models import TenantUser, User
from tests.utils import assertions


@pytest.mark.django_db
class TestCurrentUser:
  @pytest.fixture(autouse=True)
  def _setup(self, token_pair_factory, api_client_factory):
    access, refresh, self.user, *_ = token_pair_factory()
    self.api_client = api_client_factory(token=access)

  def test_fetch_current_user(self, api_reverse):
    url = api_reverse('current_user')
    resp = self.api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    expected = User.objects.get(pk=self.user.pk)
    assertions.assert_response_matches(
      data=data,
      expected=expected,
      fields=[
        'id',
        'email',
        'first_name',
        'last_name',
        'headline',
        'location',
        'locale',
        'timezone_code',
        'status',
      ],
      allow_extra=True,
      allow_missing=True,
    )

  def test_anonymous_cannot_fetch_current_user(self, api_reverse, anon_client):
    url = api_reverse('current_user')
    resp = anon_client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserTenantList:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse):
    self.url = api_reverse('current_user_tenants')
    self.page_size = 5

  def test_get_tenants(self, auth_ctx_factory, tenant_user_factory):
    user, tenant_user, api_client, api_tenant = auth_ctx_factory(
      role='member', tenant_relation='same')
    for _ in range(self.page_size):
      tenant_user_factory(user=user)

    resp = api_client.get(self.url, { 'page': 1, 'page_size': self.page_size })

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    query = TenantUser.available.filter(user_id=user.id)
    assertions.assert_mapping_value_type(
      data=data,
      key='results',
      expected_type=list,
    )
    assertions.assert_mapping_value(
      data=data,
      key='count',
      expected_type=int,
      expected=query.count(),
    )
    assert len(data['results']) == self.page_size

  def test_cannot_get_deleted_tenants(
      self, auth_ctx_factory, tenant_user_factory):
    user, tenant_user, api_client, api_tenant = auth_ctx_factory(
      role='member', tenant_relation='same')
    new_tenant_user = tenant_user_factory(user=user)
    new_tenant_user.tenant.delete()

    resp = api_client.get(self.url, { 'page': 1, 'page_size': self.page_size })

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    query = TenantUser.available.filter(user_id=user.id)
    assertions.assert_mapping_value_type(
      data=data,
      key='results',
      expected_type=list,
    )
    assertions.assert_mapping_value(
      data=data,
      key='count',
      expected_type=int,
      expected=query.count(),
    )
    assert len(data['results']) == 1

  def test_anonymous_cannot_get_tenants(self, anon_client):
    resp = anon_client.get(self.url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
