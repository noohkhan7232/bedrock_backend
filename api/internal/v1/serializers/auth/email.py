from django.conf import settings
from rest_framework import serializers

from api.base.serializers import BaseSerializer


class EmailAvailabilitySerializer(BaseSerializer):
  email = serializers.EmailField(
    max_length=255,
    required=False,
    write_only=True,
  )
  is_available = serializers.BooleanField(
    read_only=True,
    help_text=(
      'True indicates the email address is not registered and '
      'is available for sign-up.'
    ),
  )


class EmailVerificationCodeSerializer(BaseSerializer):
  email = serializers.EmailField(write_only=True)
  email_sent = serializers.BooleanField(
    read_only=True,
    help_text=(
      'Indicates a sign-up link has been sent to the provided email.'
    ),
  )


class EmailVerificationCodeEmailSerializer(BaseSerializer):
  verification_code = serializers.CharField(
    max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH,
    write_only=True,
    help_text=(
      'The unique code provided in the sign-up link sent by '
      '`email_verification_code` API.'
    ),
  )
  email = serializers.EmailField(read_only=True)
