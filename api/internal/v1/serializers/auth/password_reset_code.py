from django.conf import settings
from rest_framework import serializers

from api.base.serializers import BaseSerializer


class PasswordResetCodeSerializer(BaseSerializer):
  email = serializers.EmailField(
    max_length=255,
    required=False,
    write_only=True,
  )
  email_sent = serializers.BooleanField(
    read_only=True,
    help_text=(
      'Indicate an email with the password reset link has been sent.'
    ),
  )
  message = serializers.CharField(read_only=True)


class PasswordResetSerializer(BaseSerializer):
  email = serializers.EmailField(write_only=True)
  reset_code = serializers.CharField(
    max_length=settings.PASSWORD_RESET_CODE_LENGTH,
    write_only=True,
    help_text=(
      'The unique code provided in the password reset link sent by '
      '`password_reset_code` API.'
    ),
  )
  password = serializers.CharField(
    max_length=255, write_only=True, help_text='New password.')

  message = serializers.CharField(read_only=True)
  password_reset = serializers.BooleanField(
    read_only=True,
    help_text='True if password was successfully reset.',
  )


class PasswordResetCodeEmailSerializer(BaseSerializer):
  reset_code = serializers.CharField(
    write_only=True,
    help_text=(
      'The unique code provided in the password reset link sent by '
      '`password_reset_code` API.'
    ),
  )
  email = serializers.EmailField(max_length=255, read_only=True)
  message = serializers.CharField(read_only=True)
