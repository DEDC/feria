from django.urls import path
from rest_framework import routers
from apps.dates.views import get_available_dates, get_available_times
# admin
from apps.admin.views import render_nave1

# router = routers.SimpleRouter()
# router.register('get-available-dates', get_available_dates)
# urlpatterns = router.urls

urlpatterns = [
    # path('get-available-dates', get_available_dates),
    # path('get-available-times/<str:date>', get_available_times),
    path('nave/1/data', render_nave1)
]