from django.urls import path

from api.internal.v1.urls import agent, auth, tenant, user
from api.internal.v1.views.share import ShareView

app_name = 'internal_api_v1'

urlpatterns = (
  [
    path(
      'shares/',
      ShareView.as_view(),
      name='shares',
    ),
  ]
  + auth.urlpatterns
  + agent.urlpatterns
  + tenant.urlpatterns
  + user.urlpatterns
)
