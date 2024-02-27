from django.urls import path
from apps.dates.views import get_available_dates, get_available_times
# admin
from apps.admin.views import render_place

urlpatterns = [
    path('get-available-dates', get_available_dates),
    path('get-available-times/<str:date>', get_available_times),
    path('places/<str:key>/data', render_place)
]