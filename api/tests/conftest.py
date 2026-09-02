import re
from pathlib import PurePosixPath

import pytest
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import SSOEmailDomain, TenantUser
from tests.constants import (
  DEFAULTS,
  TENANT_USER_ROLE_MAP,
)
from tests.factories.tenant_user_factory import TenantUserFactory


_API_VERSION_RE = re.compile(r'(?:^|/)(?:tests/)?v(?P<num>\d+)(?:/|$)')

@pytest.fixture
def api_version(request):
  nodeid = request.node.nodeid.replace('\\', '/')
  m = _API_VERSION_RE.search(nodeid)
  return f"v{m.group('num')}" if m else None

@pytest.fixture
def api_visibility(request):
  path = request.node.nodeid.replace('\\', '/').split('::', 1)[0]
  parts = set(PurePosixPath(path).parts)
  if 'internal' in parts:
    return 'internal'
  elif 'external' in parts:
    return 'external'
  return None

@pytest.fixture
def api_reverse(api_version, api_visibility):
  """
  Usage: url = api_reverse('token_pair')
  Builds reverse('api:{version}:token_pair').
  """
  def api_reverse_impl(
      name,
      args=None,
      kwargs=None,
      current_app=None,
      namespace='api',
  ):
    url = reverse(
      f'{namespace}:{api_visibility}:{api_version}:{name}',
      args=args,
      kwargs=kwargs,
      current_app=current_app,
    )
    return url
  return api_reverse_impl

@pytest.fixture
def api_client_factory():
  def _create(
      *,
      token: str | None = None,
      auth_header: str = 'Bearer',
      default_format: str = 'json',
  ):
    client = APIClient()
    client.default_format = default_format
    if token:
      client.credentials(HTTP_AUTHORIZATION=f'{auth_header} {token}')
    return client
  return _create

@pytest.fixture
def token_pair_factory(
    api_reverse,
    api_client_factory,
    user_factory,
    tenant_user_factory,
):
  def _create(
      *,
      user=None,
      tenant_user=None,
      tenant=None,
      email=None,
      password=DEFAULTS.PASSWORD,
  ):
    if tenant_user:
      user = tenant_user.user
    elif user is None:
      kwargs = { 'password': make_password(password) }
      if email is not None:
        kwargs['email'] = email
      user = user_factory(**kwargs)

    api_client = api_client_factory()
    url = api_reverse('token_pair')
    resp = api_client.post(url, { 'email': user.email, 'password': password })
    assert resp.status_code == status.HTTP_200_OK, resp.content

    data = resp.json()
    return data['access'], data['refresh'], user
  return _create

@pytest.fixture
def auth_ctx_factory(
    api_client_factory,
    token_pair_factory,
    tenant_factory,
    default_seed,
):
  """
  Builds: (user, user_tenant_user, api_client, api_tenant)

  - api_tenant - tenant domain used in the endpoint.
  - user_tenant - tenant the user is currently operating under.
  """
  def _create(
      *,
      role: str = 'member',
      tenant_relation: str = 'same',
      plan: str = 'free',
      use_seed: bool = True,
      api_tenant = None,
  ):
    """
    role: 'admin' | 'manager' | 'member'
    tenant_relation:
      'same'  -> user belongs only to api_tenant
      'other' -> user belongs only to a different tenant
      'both'  -> user belongs to api_tenant and another tenant
    """
    if api_tenant is None:
      if use_seed:
        api_tenant = default_seed.tenants[plan][0]
      else:
        api_tenant = tenant_factory(plan=plan)

    if tenant_relation == 'same':
      user_tenant = api_tenant
    else:
      user_tenant = (
        default_seed.tenants[plan][1]
        if use_seed else tenant_factory(plan=plan)
      )

    tenant_user = None
    role_uid = TENANT_USER_ROLE_MAP[role].uid
    if use_seed:
      tenant_user = (
        TenantUser.available
          .filter(tenant_id=user_tenant.id, role_uid=role_uid)
          .first()
      )
    else:
      tenant_user = TenantUserFactory(role=role, tenant=user_tenant)
    user = tenant_user.user

    if tenant_relation == 'both' and user_tenant != api_tenant:
      TenantUserFactory(role=role, tenant=api_tenant, user=user)

    access, *_ = token_pair_factory(user=user)
    api_client = api_client_factory(token=access)

    return user, tenant_user, api_client, api_tenant
  return _create

@pytest.fixture
def sso_email_domain_factory():
  def _create(email_or_domain, connection_id='dummy'):
    domain = email_or_domain.split('@')[-1]
    SSOEmailDomain.objects.create(**{
      'domain': domain,
      'connection_id': connection_id,
    })
  return _create

@pytest.fixture
def anon_client(api_client_factory):
  return api_client_factory()

@pytest.fixture
def auth_client(api_client_factory, token_pair_factory):
  access, *_ = token_pair_factory()
  return api_client_factory(token=access)

@pytest.fixture
def login(api_reverse, anon_client):
  def _create(email, password):
    url = api_reverse('token_pair')
    payload = { 'email': email, 'password': password }
    resp = anon_client.post(url, payload)
    return resp
  return _create

@pytest.fixture(autouse=True)
def clear_outbox():
  mail.outbox.clear()
  yield
  mail.outbox.clear()
