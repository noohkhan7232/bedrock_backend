from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.base.serializers import BaseModelSerializer, BaseSerializer
from api.internal.v1.serializers.auth.token import TokenPairSerializer
from api.schema.decorators import (
  extend_method_field_schema,
  extend_serializer_schema,
)
from core.constants.language import APP_LANGUAGE_CODE_CHOICES
from core.constants.timezone import APP_TIMEZONE_CODE_CHOICES
from core.models import SSOEmailDomain, User
from core.services.user.language import get_user_languages
from core.services.user.link import get_user_links
from core.utils.email import get_email_domain


@extend_serializer_schema(exclude_fields=('ip_address',))
class NewUserSerializer(BaseModelSerializer):
  """
  The invitation_code could be utilized to verify that the provided
  email is eligible for signup, based on its association with
  invitation_code.
  Importantly, this class doesn't handle the creation of tenant_user
  record directly. It should be performed externally,
  outside the scope of this class.
  """
  email = serializers.CharField(max_length=255, write_only=True)
  first_name = serializers.CharField(max_length=255, write_only=True)
  last_name = serializers.CharField(max_length=255, write_only=True)
  password = serializers.CharField(allow_blank=True, write_only=True)
  headline = serializers.CharField(max_length=255, write_only=True)
  location = serializers.CharField(
    max_length=255, write_only=True, allow_blank=True, default='')
  invitation_code = serializers.CharField(
    max_length=settings.TENANT_INVITATION_CODE_LENGTH,
    required=False, allow_null=True, allow_blank=True,
    write_only=True, help_text='Required if verification_code is not given.')
  verification_code = serializers.CharField(
    max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH,
    required=False, allow_null=True, allow_blank=True,
    write_only=True, help_text='Required if invitation_code is not given.')
  sso_code = serializers.CharField(
    max_length=255, required=False, allow_null=True, allow_blank=True,
    write_only=True, help_text='Required if SSO user.')
  ip_address = serializers.CharField(
    max_length=64, required=False, allow_null=True, allow_blank=True,
    write_only=True)

  token_pair = TokenPairSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = User
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'status',
    )
    exclude = BaseModelSerializer.Meta.exclude + (
      'groups',
      'user_permissions',
    )


class BaseUserSerializer(BaseModelSerializer):
  languages = serializers.SerializerMethodField()
  links = serializers.SerializerMethodField()

  locale = serializers.ChoiceField(
    choices=APP_LANGUAGE_CODE_CHOICES,
    required=False,
  )
  timezone_code = serializers.ChoiceField(
    choices=APP_TIMEZONE_CODE_CHOICES,
    required=False,
  )

  class Meta(BaseModelSerializer.Meta):
    model = User
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'email',
      'status',
    )
    exclude = BaseModelSerializer.Meta.exclude + (
      'password',
      'is_superuser',
      'is_staff',
      'is_active',
      'disable_promotion',
      'groups',
      'user_permissions',
    )

  def get_languages(self, obj):
    return get_user_languages(user_id=obj.id)

  def get_links(self, obj):
    return get_user_links(user_id=obj.id)


class UserSerializer(BaseUserSerializer):
  class Meta(BaseUserSerializer.Meta):
    read_only_fields = BaseUserSerializer.Meta.read_only_fields + (
      'image',
    )


class CurrentUserSerializer(BaseUserSerializer):
  sso_required = serializers.SerializerMethodField()

  class Meta(BaseUserSerializer.Meta):
    read_only_fields = BaseUserSerializer.Meta.read_only_fields + (
      'image',
    )

  @extend_method_field_schema(bool)
  def get_sso_required(self, obj):
    domain = get_email_domain(email=obj.email)
    if len(domain) == 0:
      raise ValidationError('Email domain not found.')
    return SSOEmailDomain.objects.filter(domain__iexact=domain).exists()


class CurrentUserUpdateSerializer(BaseUserSerializer):
  class Meta(BaseUserSerializer.Meta):
    exclude = None
    fields = (
      'first_name',
      'last_name',
      'headline',
      'location',
      'locale',
      'timezone_code',
      'disable_promotion',
    )


@extend_serializer_schema(exclude_fields=('user_id',))
class CurrentUserEmailSerializer(BaseSerializer):
  user_id = serializers.IntegerField(write_only=True)
  email = serializers.CharField(read_only=True)


@extend_serializer_schema(exclude_fields=('user_id',))
class CurrentUserImageUpdateSerializer(BaseSerializer):
  user_id = serializers.IntegerField(write_only=True)
  image = serializers.ImageField(write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


@extend_serializer_schema(exclude_fields=('user_id',))
class CurrentUserPasswordSerializer(BaseSerializer):
  user_id = serializers.IntegerField(write_only=True)
  password = serializers.CharField(
    min_length=8, max_length=255, write_only=True)
  new_password = serializers.CharField(
    min_length=8, max_length=255, write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


@extend_serializer_schema(exclude_fields=('actor_user_id',))
class CurrentUserDeleteSerializer(BaseSerializer):
  actor_user_id = serializers.IntegerField(write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['actor_user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)
