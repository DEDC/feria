# Django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('apps.users.urls', namespace='users')),
    path('p/', include('apps.places.urls', namespace='places')),
    path('api/', include('apps.dates.urls')),
    path('admin/', include('apps.admin.urls', namespace='admin')),
    path('__debug__/', include('debug_toolbar.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)