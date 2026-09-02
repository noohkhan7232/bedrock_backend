from django.urls import path

from api.internal.v1.views.auth import (
  EmailAvailabilityView,
  EmailVerificationCodeEmailView,
  EmailVerificationCodeView,
  PasswordResetCodeEmailView,
  PasswordResetCodeView,
  PasswordResetView,
  SsoAuthorizationUrlView,
  SsoEnablementStatusView,
  TokenPairView,
  TokenRefreshView,
  TokenRevokeView,
)
from api.internal.v1.views.tenant_invitation_code import (
  TenantInvitationCodeEmailView,
  TenantInvitationCodeTenantView,
)


app_name = 'internal_api_v1_auth'

urlpatterns = [
  path(
    'auth/email/availability/',
    EmailAvailabilityView.as_view(),
    name='email_availability',
  ),
  path(
    'auth/email/code/verification/',
    EmailVerificationCodeView.as_view(),
    name='email_verification',
  ),
  path(
    'auth/email/code/password-reset/',
    PasswordResetCodeView.as_view(),
    name='password_reset_code',
  ),
  path(
    'auth/password-reset/',
    PasswordResetView.as_view(),
    name='password_reset',
  ),
  path(
    'auth/sso/authorization-url/',
    SsoAuthorizationUrlView.as_view(),
    name='sso_authorization_url',
  ),
  path(
    'auth/sso/enablement/status/',
    SsoEnablementStatusView.as_view(),
    name='sso_enablement_status',
  ),
  path(
    'auth/token/pair/',
    TokenPairView.as_view(),
    name='token_pair',
  ),
  path(
    'auth/token/refresh/',
    TokenRefreshView.as_view(),
    name='token_refresh',
  ),
  path(
    'auth/token/revoke/',
    TokenRevokeView.as_view(),
    name='token_revoke',
  ),
  path(
    'lookup/email/email-verification-code/',
    EmailVerificationCodeEmailView.as_view(),
    name='email_verification_code_email',
  ),
  path(
    'lookup/email/password-reset-code/',
    PasswordResetCodeEmailView.as_view(),
    name='password_reset_code_email',
  ),
  path(
    'lookup/email/tenant-invitation-code/',
    TenantInvitationCodeEmailView.as_view(),
    name='tenant_invitation_code_email',
  ),
  path(
    'lookup/tenant/tenant-invitation-code/',
    TenantInvitationCodeTenantView.as_view(),
    name='tenant_invitation_code_tenant',
  ),
]
