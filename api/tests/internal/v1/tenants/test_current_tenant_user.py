import pytest
from rest_framework import status

from core.models import TenantUser
from tests.utils import assertions


@pytest.mark.django_db
class TestCurrentTenantUser:
  @pytest.fixture(autouse=True)
  def _setup(
      self,
      api_reverse,
      tenant_user_factory,
      token_pair_factory,
      api_client_factory,
  ):
    self.tenant_user = tenant_user_factory()
    self.url = api_reverse(
      'current_tenant_user',
      kwargs={'domain': self.tenant_user.tenant.domain},
    )
    access, *_ = token_pair_factory(tenant_user=self.tenant_user)
    self.api_client = api_client_factory(token=access)

  def test_fetch_current_tenant_user(self):
    resp = self.api_client.get(self.url)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    expected = TenantUser.available.get(pk=self.tenant_user.pk)
    assertions.assert_response_matches(
      data=data,
      expected=expected,
      fields=[
        'id',
        'title',
        'description',
        'disable_email_notification',
        'role_uid',
      ],
    )
    assertions.assert_mapping_key(data=data, key='user')
    user = data['user']
    assertions.assert_response_matches(
      data=user,
      expected=expected.user,
      fields=[
        'id',
        'email',
        'first_name',
        'last_name',
      ],
    )

  def test_tenantless_user_cannot_fetch_current_tenant_user(self, auth_client):
    resp = auth_client.get(self.url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

  def test_anonymous_cannot_fetch_current_tenant_user(self, anon_client):
    resp = anon_client.get(self.url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
