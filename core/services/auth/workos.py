from django.conf import settings
from workos import WorkOSClient


workos_client = WorkOSClient(
  api_key=settings.SSO_WORKOS_API_KEY,
  client_id=settings.SSO_WORKOS_CLIENT_ID,
)
