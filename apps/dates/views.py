# Django
from django.utils import formats
# DjangoRestFramework
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework.views import APIView
import requests
# dates
from apps.dates.tools import get_dates_from_range, get_times_from_range
from apps.dates.models import CitasAgendadas

all_dates = get_dates_from_range('2025-02-28', settings.END_DATES)
all_hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_available_dates(request):
    scheduled = CitasAgendadas.objects.filter(fecha__year=2025).values('fecha', 'hora')
    exclude_dates = []
    for sch in scheduled:
        if sch['fecha'].strftime('%Y-%m-%d') in all_dates:
            hours_completed = 0
            for hr in all_hours:
                modules_scheduled = scheduled.filter(fecha=sch['fecha'], hora=hr).count()
                if modules_scheduled >= settings.ATTENTION_MODULES:
                    hours_completed += 1
            if hours_completed == len(all_hours):
                exclude_dates.append(sch['fecha'].strftime('%Y-%m-%d'))
    fdates = [{'short_format': d.strftime('%Y-%m-%d'), 'text_format': formats.date_format(d, "j \d\e F \d\e Y")} for d in all_dates if d.strftime('%Y-%m-%d') not in exclude_dates]
    return Response(fdates)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_available_times(request, date):
    exclude_hours = []
    for hr in all_hours:
        modules_scheduled = CitasAgendadas.objects.filter(fecha=date, hora=hr).count()
        if modules_scheduled >= settings.ATTENTION_MODULES:
            exclude_hours.append(hr)
    fhours = [{'short_format': t} for t in all_hours if t not in exclude_hours]
    return Response(fhours)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_curp_service(request, curp):
    response = []
    headersAuth = {
        'Authorization': f'Bearer {settings.TOKEN_CURP}',
    }

    data = {
        'curp': curp
    }
    print(headersAuth)
    resp = requests.post(f"{settings.URL_CURP}consulta-curp", json=data, headers=headersAuth, verify=False, stream=False)
    if resp.status_code == 200:
        response = resp.json()
    return Response(response)
