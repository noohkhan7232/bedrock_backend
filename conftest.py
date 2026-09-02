from pytest_factoryboy import register

from tests.factories.email_verification_code_factory import (
  EmailVerificationCodeFactory,
)
from tests.factories.tenant_factory import TenantFactory
from tests.factories.tenant_user_factory import TenantUserFactory
from tests.factories.user_factory import UserFactory


register(EmailVerificationCodeFactory)
register(TenantFactory)
register(UserFactory)
register(TenantUserFactory)

pytest_plugins =['tests.fixtures']
