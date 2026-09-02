from django.urls import include, path


app_name = 'internal_api'

urlpatterns = [
  path('v1/', include('api.internal.v1.urls', namespace='v1')),
]
