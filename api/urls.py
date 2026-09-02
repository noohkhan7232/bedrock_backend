from django.urls import include, path


app_name = 'api'

urlpatterns = [
  path('api/', include('api.internal.urls', namespace='internal')),
  path('external/api/', include('api.external.urls', namespace='external')),
]
