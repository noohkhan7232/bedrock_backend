from core.models import EmailJob
from .email_verification import EmailVerificationMessage
from .password_reset import PasswordResetMessage
from .signup_welcome import SignupWelcomeMessage
from .tenant_invitation import TenantInvitationMessage


TEMPLATE_MESSAGE_CLASSES = {
  EmailJob.EmailType.EMAIL_VERIFICATION: EmailVerificationMessage,
  EmailJob.EmailType.PASSWORD_RESET: PasswordResetMessage,
  EmailJob.EmailType.SIGNUP_WELCOME: SignupWelcomeMessage,
  EmailJob.EmailType.TENANT_INVITE: TenantInvitationMessage,
}
