# Python
import datetime
# Django
from django.utils import formats
# DjangoRestFramework
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
# dates
from apps.dates.tools import get_dates_from_range, get_times_from_range
from apps.dates.models import CitasAgendadas

modules = 5
dates = get_dates_from_range('2024/3/11', '2024/3/30')
hours = get_times_from_range('9:00', '15:00', '30min')

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def get_available_dates(request):
    scheduled = CitasAgendadas.objects.filter(fecha__year=2024).values('fecha', 'hora')
    exclude_dates = []
    for sch in scheduled:
        if sch['fecha'].strftime('%Y-%m-%d') in dates:
            hours_completed = 0
            for hr in hours:
                modules_scheduled = scheduled.filter(fecha=sch['fecha'], hora=hr).count()
                if modules_scheduled >= modules:
                    hours_completed += 1
            if hours_completed == len(hours):
                exclude_dates.append(sch['fecha'].strftime('%Y-%m-%d'))
    fdates = [{'short_format': d.strftime('%Y-%m-%d'), 'text_format': formats.date_format(d, "j \d\e F \d\e Y")} for d in dates if d.strftime('%Y-%m-%d') not in exclude_dates]
    return Response(fdates)

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def get_available_times(request, date):
    exclude_hours = []
    for hr in hours:
        modules_scheduled = CitasAgendadas.objects.filter(fecha=date, hora=hr).count()
        if modules_scheduled >= modules:
            exclude_hours.append(hr)
    print(exclude_hours)
    fhours = [{'short_format': t} for t in hours if t not in exclude_hours]
    return Response(fhours)