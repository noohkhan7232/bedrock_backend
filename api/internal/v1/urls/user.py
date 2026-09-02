from django.urls import path

from api.internal.v1.views.tenant import (
  CurrentUserTenantListView,
)
from api.internal.v1.views.tenant_invitation_code import (
  CurrentUserTenantInvitationCodeAcceptView,
  CurrentUserTenantInvitationCodeDeclineView,
  CurrentUserTenantInvitationCodeListView,
)
from api.internal.v1.views.user import (
  CurrentUserEmailView,
  CurrentUserImageView,
  CurrentUserPasswordView,
  CurrentUserView,
  NewUserView,
)
from api.internal.v1.views.user_language import (
  CurrentUserLanguageListView,
  CurrentUserLanguageView,
)
from api.internal.v1.views.user_link import (
  CurrentUserLinkListView,
  CurrentUserLinkView,
)


app_name = 'internal_api_v1_user'

urlpatterns = [
  path(
    'users/current/',
    CurrentUserView.as_view(),
    name='current_user',
  ),
  path(
    'users/current/email/',
    CurrentUserEmailView.as_view(),
    name='current_user_email',
  ),
  path(
    'users/current/image/',
    CurrentUserImageView.as_view(),
    name='current_user_image',
  ),
  path(
    'users/current/password/',
    CurrentUserPasswordView.as_view(),
    name='current_user_password',
  ),
  path(
    'users/current/tenants/',
    CurrentUserTenantListView.as_view(),
    name='current_user_tenants',
  ),
  path(
    'users/current/invitation-codes/',
    CurrentUserTenantInvitationCodeListView.as_view(),
    name='current_user_tenant_invitation_codes',
  ),
  path(
    'users/current/invitation-codes/accept/',
    CurrentUserTenantInvitationCodeAcceptView.as_view(),
    name='current_user_tenant_invitation_code_accept',
  ),
  path(
    'users/current/invitation-codes/decline/',
    CurrentUserTenantInvitationCodeDeclineView.as_view(),
    name='current_user_tenant_invitation_code_decline',
  ),
  path(
    'users/current/languages/',
    CurrentUserLanguageListView.as_view(),
    name='current_user_languages',
  ),
  path(
    'users/current/languages/<int:user_language_id>/',
    CurrentUserLanguageView.as_view(),
    name='current_user_language',
  ),
  path(
    'users/current/links/',
    CurrentUserLinkListView.as_view(),
    name='current_user_links',
  ),
  path(
    'users/current/links/<int:user_link_id>/',
    CurrentUserLinkView.as_view(),
    name='current_user_link',
  ),
  path(
    'users/new/',
    NewUserView.as_view(),
    name='new_user',
  ),
]
