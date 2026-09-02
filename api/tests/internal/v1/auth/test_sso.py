import json
from urllib.parse import urlparse, parse_qs, unquote

import pytest
from django.conf import settings
from rest_framework import status

from tests.utils import assertions


@pytest.mark.django_db
class TestSsoEnablementState:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, user_factory):
    self.url = api_reverse('sso_enablement_status')
    self.user = user_factory()
    self.email_domain = self.user.email.split('@')[-1]

  def test_registered_email_domain_is_enabled_to_sso(
      self, sso_email_domain_factory, anon_client):
    sso_email_domain_factory(email_or_domain=self.user.email)
    payload = {
      'email_domain': self.email_domain,
    }

    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assertions.assert_mapping_value(
      data=data,
      key='sso_enabled',
      expected_type=bool,
      expected=True,
    )
    assertions.assert_mapping_value_type(
      data=data,
      key='message',
      expected_type=str,
    )

  def test_unregistered_email_domain_is_not_enabled_to_sso(self, anon_client):
    payload = {
      'email_domain': self.email_domain,
    }

    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assertions.assert_mapping_value(
      data=data,
      key='sso_enabled',
      expected_type=bool,
      expected=False,
    )
    assertions.assert_mapping_value_type(
      data=data,
      key='message',
      expected_type=str,
    )


@pytest.mark.django_db
class TestSsoAuthorizationUrl:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, user_factory):
    self.url = api_reverse('sso_authorization_url')
    self.user = user_factory()
    self.verification_code = 'dummy_verification_code'
    self.invitation_code = 'dummy_invitation_code'

  def test_get_authorization_url(self, sso_email_domain_factory, anon_client):
    sso_email_domain_factory(email_or_domain=self.user.email)
    payload = {
      'email': self.user.email,
      'verification_code': self.verification_code,
      'invitation_code': self.invitation_code,
    }

    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    parsed = urlparse(data['authorization_url'])
    assert parsed.scheme == 'https'

    qs = parse_qs(parsed.query)
    assertions.assert_mapping_value_type(
      data=qs,
      key='client_id',
      expected_type=list,
    )
    assert qs['client_id'][0] == 'sso_workos_client_id_dummy'
    assertions.assert_mapping_value_type(
      data=qs,
      key='redirect_uri',
      expected_type=list,
    )
    assert qs['redirect_uri'][0] == settings.SSO_REDIRECT_URI
    assertions.assert_mapping_value_type(
      data=qs,
      key='connection',
      expected_type=list,
    )
    assert qs['connection'][0] == 'dummy'
    assertions.assert_mapping_value_type(
      data=qs,
      key='response_type',
      expected_type=list,
    )
    assert qs['response_type'][0] == 'code'

    assertions.assert_mapping_value_type(
      data=qs,
      key='state',
      expected_type=list,
    )
    raw_state = qs['state'][0]
    decoded_state = unquote(raw_state)
    state = json.loads(decoded_state)
    assertions.assert_mapping_value(
      data=state,
      key='email',
      expected_type=str,
      expected=self.user.email,
    )
    assertions.assert_mapping_value(
      data=state,
      key='invitation_code',
      expected_type=str,
      expected=self.invitation_code,
    )
    assertions.assert_mapping_value(
      data=state,
      key='verification_code',
      expected_type=str,
      expected=self.verification_code,
    )

  def test_invalid_email_domain_get_empty_authorization_url(
      self, sso_email_domain_factory, anon_client):
    sso_email_domain_factory(email_or_domain=self.user.email)
    payload = {
      'email': 'anonymous@anonymous.com',
      'verification_code': self.verification_code,
      'invitation_code': self.invitation_code,
    }

    resp = anon_client.post(self.url, payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    parsed = urlparse(data['authorization_url'])
    qs = parse_qs(parsed.query)
    assert isinstance(qs, dict) and not qs
