import sys

from django.core.management.base import CommandError
from django.db import transaction

from core.constants import PLANS
from core.management.commands.base import HybridCommand
from core.models import Subscription, Tenant, TenantLimitOverride
from core.services.subscription import (
  get_tenant_plan_uid,
  get_tenant_subscription,
)


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)
    parser.add_argument(
      '--account_id',
      required=False,
      type=str,
      help='Tenant account id',
    )
    parser.add_argument(
      '--plan_uid',
      required=False,
      type=int,
      help='Plan type',
    )
    parser.add_argument(
      '--start_date',
      required=False,
      type=str,
      help='Date in MM-DD-YYYY format when the subscription starts',
    )
    parser.add_argument(
      '--end_date',
      required=False,
      type=str,
      help='Date in MM-DD-YYYY format when the subscription ends',
    )

  def handle(self, *args, **options):
    self.validate_options()

    account_id = self.option_str(
      key='account_id',
      prompt='Tenant account_id: ',
      show_input=False,
      min_length=1,
      echo=True,
    )
    plan_uid = self.option_int(
      key='plan_uid',
      prompt='Plan uid: ',
      choices=[plan.uid for plan in PLANS.as_list()],
    )
    start_date = self.option_str(
      key='start_date',
      prompt='Starts from ("MM-DD-YYYY", eg. 12-31-1999): ',
      length=10,
      show_input=True,
    )
    end_date = self.option_str(
      key='end_date',
      prompt='Expires at ("MM-DD-YYYY", eg. 12-31-2000): ',
      length=10,
      show_input=True,
    )
    subscribed_at = self.parse_date(start_date)
    expires_at = self.parse_date(end_date)

    if account_id is None:
      raise CommandError('account_id is required.')

    if plan_uid == PLANS.FREE.uid:
      subscribed_at = None
      expires_at = None

    if (
      subscribed_at is not None and
      expires_at is not None and
      expires_at < subscribed_at
    ):
      raise CommandError('--end_date must be on or after --start_date.')

    if plan_uid != PLANS.FREE.uid:
      if subscribed_at is None:
        raise CommandError('--start_date is required for paid plan.')
      if expires_at is None:
        raise CommandError('--end_date is required for paid plan.')

    try:
      tenant = Tenant.all_objects.get(account_id=account_id)
    except Tenant.DoesNotExist as e:
      raise CommandError(
        'Tenant with the given account_id was not found.'
      ) from e

    old_plan_uid = get_tenant_plan_uid(tenant_id=tenant.id)
    upgraded = old_plan_uid < plan_uid

    with transaction.atomic():
      self.update_subscription(
        tenant_id=tenant.id,
        plan_uid=plan_uid,
        subscribed_at=subscribed_at,
        expires_at=expires_at,
      )

      self.update_tenant_limit_overrides(
        tenant_id=tenant.id,
        plan_uid=plan_uid,
        upgraded=upgraded,
      )

    if not self.is_automated:
      plan_name = PLANS.get_name_by_uid(plan_uid)
      sys.stdout.write(
        f'Successfully set plan of Tenant:{tenant.name} to {plan_name}.\n'
      )
      if plan_uid != PLANS.FREE.uid:
        sys.stdout.write(
          f'Starts from: {subscribed_at}\n'
          f'Expires at: {expires_at}\n'
        )

  def update_subscription(
      self, tenant_id, plan_uid, subscribed_at, expires_at):
    req = dict(
      tenant_id=tenant_id,
      plan_uid=plan_uid,
      subscribed_at=subscribed_at,
      expires_at=expires_at,
    )
    current_subscription = get_tenant_subscription(tenant_id=tenant_id)
    if current_subscription is None:
      Subscription.objects.create(**req)
      return

    for key, value in req.items():
      setattr(current_subscription, key, value)
    current_subscription.save(
      update_fields=['plan_uid', 'subscribed_at', 'expires_at']
    )

  def update_tenant_limit_overrides(self, tenant_id, plan_uid, upgraded):
    plan = PLANS.get_by_uid(plan_uid)
    query = TenantLimitOverride.objects.filter(tenant_id=tenant_id)

    for override in query.all():
      limit_key = override.limit_key
      current_value = override.value
      plan_value = getattr(plan, limit_key)

      if plan_value is None:
        raise ValueError(f'plan_value of {limit_key} is not found.')

      if not upgraded or current_value < plan_value:
        override.delete()
