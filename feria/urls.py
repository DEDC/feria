# Django
from django.urls import path, include

urlpatterns = [
    path('', include('apps.users.urls', namespace='users')),
    path('p/', include('apps.places.urls', namespace='places')),
    path('api/', include('apps.dates.urls'))
]