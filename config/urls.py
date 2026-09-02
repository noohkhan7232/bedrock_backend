import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.urls import path, include

from api.schema import external, internal


urlpatterns = [
  path('', include('api.urls', namespace='api')),
]

if settings.INTERNAL_API_DOC_ENABLED or settings.EXTERNAL_API_DOC_ENABLED:
  urlpatterns += [path(
    settings.API_DOC_LOGIN_URL,
    include('rest_framework.urls'),
  )]

if settings.EXTERNAL_API_DOC_ENABLED or True:
  urlpatterns += [path(
    os.path.join(settings.EXTERNAL_API_DOWNLOAD_URL, 'v1/'),
    login_required(external.v1.views.APIDownloadView.as_view()),
    name='external-api-v1',
  )]
  urlpatterns += [path(
    os.path.join(settings.EXTERNAL_API_DOC_URL, 'v1/'),
    login_required(external.v1.views.APIDocView.as_view(url_name='external-api-v1')),
    name='external-api-v1-doc',
  )]

if settings.INTERNAL_API_DOC_ENABLED:
  urlpatterns += [path(
    os.path.join(settings.INTERNAL_API_DOWNLOAD_URL, 'v1/'),
    login_required(internal.v1.views.APIDownloadView.as_view()),
    name='internal-api-v1',
  )]
  urlpatterns += [path(
    os.path.join(settings.INTERNAL_API_DOC_URL, 'v1/'),
    login_required(internal.v1.views.APIDocView.as_view(url_name='internal-api-v1')),
    name='internal-api-v1-doc',
  )]

if settings.DJANGO_ADMIN_SITE_ENABLED:
  urlpatterns += [path(settings.DJANGO_ADMIN_URL, admin.site.urls)]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('', lambda r: HttpResponseNotFound())] # Decoy
