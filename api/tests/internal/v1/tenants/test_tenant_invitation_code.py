import pytest
from django.contrib.auth.hashers import make_password
from rest_framework import status

from core.models import (
  EmailJob,
  TenantBlacklistedEmailDomain,
  TenantEmailPolicyConfig,
  TenantInvitationCode,
  TenantWhitelistedEmail,
  TenantWhitelistedEmailDomain,
  TenantUser,
)
from tests.constants import TENANT_EMAIL_DEFAULT_POLICIES
from tests.utils import assertions


@pytest.fixture
def blacklisted_email_domain_factory():
  def _create(tenant_id, domain, include_subdomains):
    obj = TenantBlacklistedEmailDomain.objects.create(**{
      'tenant_id': tenant_id,
      'domain': domain,
      'include_subdomains': include_subdomains,
    })
    return obj
  return _create

@pytest.fixture
def whitelisted_email_domain_factory():
  def _create(tenant_id, domain, include_subdomains):
    obj = TenantWhitelistedEmailDomain.objects.create(**{
      'tenant_id': tenant_id,
      'domain': domain,
      'include_subdomains': include_subdomains,
    })
    return obj
  return _create

@pytest.fixture
def whitelisted_email_factory():
  def _create(tenant_id, email):
    obj = TenantWhitelistedEmail.objects.create(**{
      'tenant_id': tenant_id,
      'email': email,
    })
    return obj
  return _create

@pytest.fixture
def tenant_invitation_code_factory():
  def _create(admin, email):
    obj = TenantInvitationCode(tenant_id=admin.tenant.id, email=email)
    obj.issue_invitation(tenant_user_id=admin.id)
    obj.save()
    return obj
  return _create

@pytest.fixture
def tenant_email_policy_config_factory():
  def _create(tenant_id, default_policy_uid, email_whitelist_overrides_blacklist):
    obj = TenantEmailPolicyConfig.objects.create(**{
      'tenant_id': tenant_id,
      'default_policy_uid': default_policy_uid,
      'email_whitelist_overrides_blacklist': email_whitelist_overrides_blacklist,
    })
    return obj
  return _create

@pytest.mark.django_db
class TestTenantInvitationCode:
  @pytest.fixture(autouse=True)
  def _setup(self, api_reverse, auth_ctx_factory):
    self.user, self.admin, self.api_client, self.api_tenant = (
      auth_ctx_factory(role='admin', tenant_relation='same')
    )
    self.payload = {
      'emails': ['unknown@abc.example.com'],
    }
    self.url = api_reverse(
      'tenant_invitation_codes',
      kwargs={ 'domain': self.api_tenant.domain },
    )

  @pytest.mark.parametrize('role', ['member', 'manager'])
  def test_non_admin_user_cannot_send_invitation(self, role, auth_ctx_factory):
    _, tenant_user, api_client, *_ = (
      auth_ctx_factory(role=role, tenant_relation='same')
    )
    resp = api_client.post(self.url, self.payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.api_tenant.id,
      expected_count=0,
    )

  def test_admin_send_invitation(self):
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_200_OK
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.api_tenant.id,
      expected_count=1,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('dummy.com', False,),
      ('example.com', False,),
    ],
  )
  def test_non_whitelisted_domain_is_not_invited(
      self, domain, include_subdomains, whitelisted_email_domain_factory):
    whitelisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=0,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('abc.example.com', False,),
      ('abc.example.com', True,),
      ('example.com', True,),
    ],
  )
  def test_whitelisted_domain_is_invited(
      self, domain, include_subdomains, whitelisted_email_domain_factory):
    whitelisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_200_OK
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=1,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_blacklisted_domain_is_not_invited(
      self, domain, include_subdomains, blacklisted_email_domain_factory):
    blacklisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=0,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', False,),
      ('dummy.com', True,),
    ],
  )
  def test_non_blacklisted_domain_is_invited(
      self, domain, include_subdomains, blacklisted_email_domain_factory):
    blacklisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_200_OK
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=1,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_blacklisted_domain_wins_whitelisted_domain(
      self,
      domain,
      include_subdomains,
      blacklisted_email_domain_factory,
      whitelisted_email_domain_factory,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=0,
    )

  @pytest.mark.parametrize(
    'default_policy_uid,expected_status_code,expected_email_count',
    [
      (
        TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
        status.HTTP_200_OK,
        1,
      ),
      (
        TENANT_EMAIL_DEFAULT_POLICIES.DENY_UNLISTED.uid,
        status.HTTP_403_FORBIDDEN,
        0,
      ),
    ],
  )
  def test_default_policy_determines_invitation_without_whitelist(
      self,
      default_policy_uid,
      expected_status_code,
      expected_email_count,
      tenant_email_policy_config_factory,
  ):
    tenant_email_policy_config_factory(
      tenant_id=self.admin.tenant.id,
      default_policy_uid=default_policy_uid,
      email_whitelist_overrides_blacklist=False,
    )
    resp = self.api_client.post(self.url, self.payload)
    assert resp.status_code == expected_status_code
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=expected_email_count,
    )

  @pytest.mark.parametrize(
    (
      'domain,'
      'include_subdomains,'
      'email_whitelist_overrides_blacklist,'
      'expected_status_code,'
      'expected_email_count'
    ),
    [
      ('example.com', True, False, status.HTTP_403_FORBIDDEN, 0,),
      ('abc.example.com', True, False, status.HTTP_403_FORBIDDEN, 0,),
      ('example.com', True, True, status.HTTP_200_OK, 1,),
      ('abc.example.com', True, True, status.HTTP_200_OK, 1,),
    ],
  )
  def test_whitelisted_email_overrides_blacklist_if_configured(
      self,
      domain,
      include_subdomains,
      email_whitelist_overrides_blacklist,
      expected_status_code,
      expected_email_count,
      blacklisted_email_domain_factory,
      whitelisted_email_factory,
      tenant_email_policy_config_factory,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.admin.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_factory(
      tenant_id=self.admin.tenant.id,
      email=self.payload['emails'][0],
    )
    tenant_email_policy_config_factory(
      tenant_id=self.admin.tenant.id,
      default_policy_uid=TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
      email_whitelist_overrides_blacklist=email_whitelist_overrides_blacklist,
    )

    resp = self.api_client.post(self.url, self.payload)
    assert resp.status_code == expected_status_code
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.TENANT_INVITE,
      to_emails=[self.payload['emails'][0]],
      tenant_id=self.admin.tenant.id,
      expected_count=expected_email_count,
    )


@pytest.mark.django_db
class TestExistingUserJoinTenant:
  @pytest.fixture(autouse=True)
  def _setup(
      self,
      api_reverse,
      auth_ctx_factory,
      user_factory,
      token_pair_factory,
      api_client_factory,
      tenant_invitation_code_factory,
  ):
    self.url = api_reverse('current_user_tenant_invitation_code_accept')
    _, self.admin, _, self.tenant = (
      auth_ctx_factory(role='admin', tenant_relation='same')
    )

    self.sub = 'abc'
    self.domain = 'example.com'
    self.fulldomain = f'{self.sub}.{self.domain}'
    self.user = user_factory(
      email=f'localtestuser@{self.fulldomain}',
      password=make_password('Pa$$w0rd!'),
    )
    access, *_ = token_pair_factory(user=self.user)
    self.api_client = api_client_factory(token=access)
    self.payload = {
      'invitation_code': (
        tenant_invitation_code_factory(
          admin=self.admin, email=self.user.email
        ).invitation_code
      )
    }

  def test_user_accepts_invitation(self):
    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert query.exists()
    data = resp.json()
    assertions.assert_mapping_value(
      data=data,
      key='id',
      expected_type=int,
      expected=self.tenant.id,
    )

  def test_user_cannot_accept_invitation_with_invalid_code(self):
    self.payload['invitation_code'] = 'invalid_invitation_code'
    resp = self.api_client.post(self.url, self.payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert not query.exists()

  def test_other_user_cannot_accept_invitation(
      self,
      user_factory,
      token_pair_factory,
      api_client_factory,
  ):
    other_user = user_factory(password=make_password('Pa$$w0rd!'))
    access, *_ = token_pair_factory(user=other_user)
    other_api_client = api_client_factory(token=access)

    resp = other_api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('dummy.com', False,),
      ('example.com', False,),
    ],
  )
  def test_user_cannot_accept_invitation_if_domain_is_not_whitelisted(
      self,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', True,),
    ],
  )
  def test_user_accepts_invitation_with_whitelisted_domain(
      self,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert query.exists()
    data = resp.json()
    assertions.assert_mapping_value(
      data=data,
      key='id',
      expected_type=int,
      expected=self.tenant.id,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_user_cannot_accept_invitation_with_blacklisted_domain(
      self,
      blacklisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', False,),
      ('dummy.com', True,),
    ],
  )
  def test_user_accepts_invitation_with_non_blacklisted_domain(
      self,
      blacklisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert query.exists()

    data = resp.json()
    assertions.assert_mapping_value(
      data=data,
      key='id',
      expected_type=int,
      expected=self.tenant.id,
    )

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_blacklisted_domain_wins_whitelisted_domain(
      self,
      blacklisted_email_domain_factory,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.user.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'default_policy_uid,expected_status_code',
    [
      (
        TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
        status.HTTP_201_CREATED,
      ),
      (
        TENANT_EMAIL_DEFAULT_POLICIES.DENY_UNLISTED.uid,
        status.HTTP_403_FORBIDDEN,
      ),
    ],
  )
  def test_default_policy_determines_acceptability_without_whitelist(
      self,
      default_policy_uid,
      expected_status_code,
      tenant_email_policy_config_factory,
  ):
    tenant_email_policy_config_factory(
      tenant_id=self.admin.tenant.id,
      default_policy_uid=default_policy_uid,
      email_whitelist_overrides_blacklist=False,
    )
    resp = self.api_client.post(self.url, self.payload)
    assert resp.status_code == expected_status_code
    if resp.status_code >= 400:
      assert not TenantUser.all_objects.filter(
        tenant_id=self.tenant.id,
        user__email=self.user.email,
      ).exists()
    else:
      assert TenantUser.available.filter(
        tenant_id=self.tenant.id,
        user__email=self.user.email,
      ).exists()

  @pytest.mark.parametrize(
    (
      'domain,'
      'include_subdomains,'
      'email_whitelist_overrides_blacklist,'
      'expected_status_code,'
    ),
    [
      ('example.com', True, False, status.HTTP_403_FORBIDDEN,),
      ('abc.example.com', True, False, status.HTTP_403_FORBIDDEN,),
      ('example.com', True, True, status.HTTP_201_CREATED,),
      ('abc.example.com', True, True, status.HTTP_201_CREATED,),
    ],
  )
  def test_user_accepts_invitation_with_whitelisted_email(
      self,
      domain,
      include_subdomains,
      email_whitelist_overrides_blacklist,
      expected_status_code,
      blacklisted_email_domain_factory,
      whitelisted_email_factory,
      tenant_email_policy_config_factory,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_factory(
      tenant_id=self.tenant.id,
      email=self.user.email,
    )
    tenant_email_policy_config_factory(
      tenant_id=self.tenant.id,
      default_policy_uid=TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
      email_whitelist_overrides_blacklist=email_whitelist_overrides_blacklist,
    )

    resp = self.api_client.post(self.url, self.payload)

    assert resp.status_code == expected_status_code
    if resp.status_code >= 400:
      assert not TenantUser.all_objects.filter(
        tenant_id=self.tenant.id,
        user__email=self.user.email,
      ).exists()
    else:
      assert TenantUser.available.filter(
        tenant_id=self.tenant.id,
        user__email=self.user.email,
      ).exists()


@pytest.mark.django_db
class TestNewUserJoinTenant:
  @pytest.fixture(autouse=True)
  def _setup(
      self,
      api_reverse,
      auth_ctx_factory,
      user_factory,
      token_pair_factory,
      api_client_factory,
      tenant_invitation_code_factory,
  ):
    self.url = api_reverse('new_user')
    _, admin, _, self.tenant = (
      auth_ctx_factory(role='admin', tenant_relation='same')
    )

    sub = 'abc'
    domain = 'example.com'
    fulldomain = f'{sub}.{domain}'
    self.email = f'localnewuser@{fulldomain}'

    tenant_invitation_code = (
      tenant_invitation_code_factory(admin=admin, email=self.email)
    )

    self.payload = {
      'first_name': 'Foo',
      'last_name': 'Var',
      'email': self.email,
      'password': 'Pa$$w0rd!',
      'headline': 'test headline',
      'location': 'test location',
      'verification_code': '',
      'invitation_code': tenant_invitation_code.invitation_code,
      'sso_code': '',
    }

  def test_signup_and_join_succeeds(self, anon_client):
    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=1,
    )
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert query.exists()

  def test_signup_fails_with_invalid_invitation_code(self, anon_client):
    self.payload['invitation_code'] = 'invalid_invitation_code'

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_410_GONE
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=0,
    )
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert not query.exists()

  def test_signup_fails_with_invalid_email(self, anon_client):
    self.payload['email'] = 'invalidemail@example.com'

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_410_GONE
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=0,
    )
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains,',
    [
      ('dummy.com', False,),
      ('example.com', False,),
    ],
  )
  def test_signup_fails_if_domain_is_not_whitelisted(
      self,
      anon_client,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=0,
    )
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains,',
    [
      ('example.com', True,),
      ('abc.example.com', True,),
    ],
  )
  def test_signup_succeeds_with_whitelisted_domain(
      self,
      anon_client,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=1,
    )
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_signup_fails_with_blacklisted_domain(
      self,
      anon_client,
      blacklisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=0,
    )
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', False,),
      ('dummy.com', True,),
    ],
  )
  def test_user_accepts_invitation_with_non_blacklisted_domain(
      self,
      anon_client,
      blacklisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_201_CREATED
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=1,
    )
    query = TenantUser.available.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert query.exists()

  @pytest.mark.parametrize(
    'domain,include_subdomains',
    [
      ('example.com', True,),
      ('abc.example.com', False,),
    ],
  )
  def test_blacklisted_domain_wins_whitelisted_domain(
      self,
      anon_client,
      blacklisted_email_domain_factory,
      whitelisted_email_domain_factory,
      domain,
      include_subdomains,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assertions.assert_email_jobs_created(
      email_type=EmailJob.EmailType.SIGNUP_WELCOME,
      to_emails=[self.email],
      tenant_id=self.tenant.id,
      expected_count=0,
    )
    query = TenantUser.all_objects.filter(
      tenant_id=self.tenant.id, user__email=self.email)
    assert not query.exists()

  @pytest.mark.parametrize(
    'default_policy_uid,expected_status_code',
    [
      (
        TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
        status.HTTP_201_CREATED,
      ),
      (
        TENANT_EMAIL_DEFAULT_POLICIES.DENY_UNLISTED.uid,
        status.HTTP_403_FORBIDDEN,
      ),
    ],
  )
  def test_default_policy_determines_acceptability_without_whitelist(
      self,
      anon_client,
      default_policy_uid,
      expected_status_code,
      tenant_email_policy_config_factory,
  ):
    tenant_email_policy_config_factory(
      tenant_id=self.tenant.id,
      default_policy_uid=default_policy_uid,
      email_whitelist_overrides_blacklist=False,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == expected_status_code
    if resp.status_code >= 400:
      assert not TenantUser.all_objects.filter(
        tenant_id=self.tenant.id,
        user__email=self.email,
      ).exists()
    else:
      assert TenantUser.available.filter(
        tenant_id=self.tenant.id,
        user__email=self.email,
      ).exists()

  @pytest.mark.parametrize(
    (
      'domain,'
      'include_subdomains,'
      'email_whitelist_overrides_blacklist,'
      'expected_status_code,'
    ),
    [
      ('example.com', True, False, status.HTTP_403_FORBIDDEN,),
      ('abc.example.com', True, False, status.HTTP_403_FORBIDDEN,),
      ('example.com', True, True, status.HTTP_201_CREATED,),
      ('abc.example.com', True, True, status.HTTP_201_CREATED,),
    ],
  )
  def test_user_accepts_invitation_with_whitelisted_email(
      self,
      anon_client,
      domain,
      include_subdomains,
      email_whitelist_overrides_blacklist,
      expected_status_code,
      blacklisted_email_domain_factory,
      whitelisted_email_factory,
      tenant_email_policy_config_factory,
  ):
    blacklisted_email_domain_factory(
      tenant_id=self.tenant.id,
      domain=domain,
      include_subdomains=include_subdomains,
    )
    whitelisted_email_factory(
      tenant_id=self.tenant.id,
      email=self.email,
    )
    tenant_email_policy_config_factory(
      tenant_id=self.tenant.id,
      default_policy_uid=TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
      email_whitelist_overrides_blacklist=email_whitelist_overrides_blacklist,
    )

    resp = anon_client.post(self.url, self.payload)

    assert resp.status_code == expected_status_code
    if resp.status_code >= 400:
      assert not TenantUser.all_objects.filter(
        tenant_id=self.tenant.id,
        user__email=self.email,
      ).exists()
    else:
      assert TenantUser.available.filter(
        tenant_id=self.tenant.id,
        user__email=self.email,
      ).exists()
