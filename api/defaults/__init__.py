from api.base.defaults import BaseFromRequestDefault


class CurrentTenantDefault(BaseFromRequestDefault):
  def __call__(self, serializer_field):
    return self._get_value_from_request(serializer_field, 'tenant')


class CurrentTenantUserDefault(BaseFromRequestDefault):
  def __call__(self, serializer_field):
    return self._get_value_from_request(serializer_field, 'tenant_user')
