from django.urls import include, path


app_name = 'external_api'

urlpatterns = [
  path('v1/', include('api.external.v1.urls', namespace='v1')),
]
