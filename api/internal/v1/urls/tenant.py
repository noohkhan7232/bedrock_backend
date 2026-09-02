from django.urls import path

from api.internal.v1.views.tenant import (
  NewTenantView,
  TenantView,
)
from api.internal.v1.views.tenant_invitation_code import (
  TenantInvitationCodeListView,
  TenantInvitationCodeView,
)
from api.internal.v1.views.tenant_user import (
  CurrentTenantUserView,
  TenantUserAutocompleteView,
  TenantUserListView,
  TenantUserRoleView,
  TenantUserView,
)

app_name = 'internal_api_v1_tenant'

tenant_url = 'tenants/<str:domain>/'

urlpatterns = [
  path(
    'tenants/new/',
    NewTenantView.as_view(),
    name='new_tenant',
  ),
  path(
    tenant_url,
    TenantView.as_view(),
    name='tenant',
  ),
  path(
    tenant_url + 'invitation-codes/',
    TenantInvitationCodeListView.as_view(),
    name='tenant_invitation_codes',
  ),
  path(
    tenant_url + 'invitation-codes/<int:tenant_invitation_code_id>/',
    TenantInvitationCodeView.as_view(),
    name='tenant_invitation_code',
  ),
  path(
    tenant_url + 'users/',
    TenantUserListView.as_view(),
    name='tenant_users',
  ),
  path(
    tenant_url + 'users/autocomplete/',
    TenantUserAutocompleteView.as_view(),
    name='tenant_user_autocomplete',
  ),
  path(
    tenant_url + 'users/current/',
    CurrentTenantUserView.as_view(),
    name='current_tenant_user',
  ),
  path(
    tenant_url + 'users/<int:tenant_user_id>/',
    TenantUserView.as_view(),
    name='tenant_user',
  ),
  path(
    tenant_url + 'users/<int:tenant_user_id>/role/',
    TenantUserRoleView.as_view(),
    name='tenant_user_role',
  ),
]
