from datetime import datetime, timezone, timedelta

from django.db.models import Exists, OuterRef, Q
from django_extensions.management.jobs import DailyJob

from core.models import TenantInvitationCode, TenantUser


class Job(DailyJob):
  help = 'Remove invitation codes whose e-mail already belongs to a tenant user.'

  BATCH_SIZE=5_000

  def execute(self):
    now = datetime.now(timezone.utc)
    query = (
      TenantInvitationCode.objects
        .annotate(
          email_exists=Exists(
            # Use objects: Inactive memberships still count as already belonging,
            # so invitations to inactive-bu-alive members can be removed.
            TenantUser.objects.filter(
              tenant_id=OuterRef('tenant_id'),
              user__email__iexact=OuterRef('email'),
            )
          ),
          has_available_tenant_users=Exists(
            TenantUser.available.filter(
              tenant_id=OuterRef('tenant_id'),
            )
          ),
        )
        .filter(
          Q(email_exists=True)
          | Q(has_available_tenant_users=False)
          | Q(valid_until__lt=now - timedelta(days=1))
        )
    )

    while True:
      ids = list(
        query
          .order_by('id')
          .values_list('id', flat=True)[: self.BATCH_SIZE]
      )
      if not ids:
        break
      TenantInvitationCode.objects.filter(id__in=ids).delete()
