# Django
import uuid
from decimal import Decimal

from django.views.generic import TemplateView, DetailView, UpdateView, RedirectView, ListView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.http import Http404
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
# DjangoRestFramework
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.dates.tools import get_dates_from_range, get_times_from_range
# places
from apps.places.models import Solicitudes, Comercios, Validaciones, Lugares, ProductosExtras, Pagos, Estacionamiento, \
    HistorialTapy, SubGiros
from apps.places.forms import RequestForm, ShopForm, ParkingForm
from apps.tpay.tools import sendEmail
from apps.tpay.views import return_html_accept, return_html_rejected
# users
from apps.users.models import Usuarios
from apps.users.forms import UserUpdateForm
# dates
from apps.dates.models import CitasAgendadas
# utils
from utils.naves import nave1, nave2, nave3, zona_a, zona_b, zona_c, zona_d, sabor_tabasco, teatro
from utils.permissions import AdminPermissions, AdminStaffPermissions
from utils.date import get_date_constancy
from utils.gafete import get_gafete
from utils.suministros import get_suministros
from utils.tarjeton import get_tarjeton
from utils.pase_caja import get_receipt
from utils.word_writer import generate_physical_document
from utils.reports import get_report, get_requests_report, get_stands_report
from utils.email import send_html_mail
from datetime import datetime

places_dict = {'n_1': nave1, 'n_2': nave2, 'n_3': nave3, 'z_a': zona_a, 'z_b': zona_b, 'z_c': zona_c, 'z_d': zona_d, 's_t': sabor_tabasco, 'teatro': teatro}

place_concept_des = {
    "1045": [1069, 90000], "1046": [1070, 83700], "1047": [1071, 81000], "1048": [1072, 72000], "1049": [1073, 63000],
    "1050": [1074, 54000], "1051": [1075, 45000], "1052": [1076, 31500], "1053": [1077, 30150], "1054": [1078, 27000],
    "1055": [1079, 23400], "1056": [1080, 22500], "1057": [1081, 20250], "1058": [1082, 18000], "1059": [1083, 15300],
    "1060": [1084, 13500], "1061": [1085, 12600], "1062": [1086, 11250], "1063": [1087, 9000], "1064": [1088, 7200],
    "1065": [1089, 6300], "1066": [1090, 3150], "1067": [1091, 2700], "1068": [1092, 2250]
}

place_concept_alcohol = {
    "1045": [1093, 115000], "1046": [1094, 108000], "1047": [1095, 105000], "1048": [1096, 95000], "1049": [1097, 85000],
    "1050": [1098, 75000], "1051": [1099, 65000], "1052": [1100, 45000], "1053": [0, 0], "1054": [1101, 40000],
    "1055": [0, 0], "1056": [1101, 40000], "1057": [0, 0], "1058": [1102, 35000], "1059": [1104, 32000],
    "1060": [1103, 30000], "1061": [1107, 22000], "1062": [1105, 25000], "1063": [0, 0], "1064": [1108, 15000],
    "1065": [1108, 15000], "1066": [0, 0], "1067": [0, 0], "1068": [0, 0]
}


ambulante_concept = {
    "amb_1": [1068, 2500], "amb_2": [1067, 3000], "amb_3": [1066, 3500]
}

dates = get_dates_from_range(settings.START_DATES, settings.END_DATES)
hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)


class Main(AdminStaffPermissions, TemplateView):
    template_name = 'admin/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().strftime('%Y-%m-%d')
        requests = Solicitudes.objects.all()
        dates = CitasAgendadas.objects.all()
        users = Usuarios.objects.all()
        validations = Validaciones.objects.all()
        branches = Comercios.objects.all()
        places = Lugares.objects.all()
        context['requests'] = requests.count()
        context['dates'] = dates.count()
        context['users'] = users.count()
        context['validations'] = validations.count()
        context['branches'] = branches.count()
        context['places'] = places.count()
        context['requests_today'] = requests.filter(fecha_reg__date=today).count()
        context['dates_today'] = dates.filter(fecha_reg__date=today).count()
        context['users_today'] = users.filter(date_joined__date=today).count()
        context['validations_today'] = validations.filter(fecha_reg__date=today).count()
        context['branches_today'] = branches.filter(fecha_reg__date=today).count()
        context['places_today'] = places.filter(fecha_reg__date=today).count()
        context['payments'] = places.filter(Q(tpay_pagado=True) | Q(caja_pago=True) | Q(transfer_pago=True)).aggregate(monto=Sum('precio'))
        context['payments_done'] = places.filter(Q(tpay_pagado=True) | Q(caja_pago=True)| Q(transfer_pago=True)).count()
        return context

class ListStands(AdminPermissions, TemplateView):
    template_name = 'admin/list_stands.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_places = Lugares.objects.all()
        metaplaces = places_dict.copy()
        count_static_places = 0
        for k, v in metaplaces.items():
            count_static_places += len(v['places'])
            for p in v['places']:
                try:
                    pbd = selected_places.get(nombre=p['text'], zona=k)
                    p['request_'] = pbd.solicitud.folio
                    p['uuid_request'] = pbd.solicitud.uuid
                    p['place'] = pbd.folio
                    p['final_price'] = pbd.precio
                    p['final_concept'] = pbd.tramite_id
                    p['is_paid'] = 'Sí' if pbd.tpay_pagado or pbd.caja_pago or pbd.transfer_pago else 'No'
                    p['alcohol'] = 'Sí' if pbd.extras.filter(tipo='licencia_alcohol').count() > 0 else 'No'
                except Lugares.DoesNotExist:
                    pass
        context['ambulantes'] = selected_places.filter(zona='amb')
        context['total_places'] = count_static_places + context['ambulantes'].count()
        context['metaplaces'] = metaplaces
        return context

class ListRequests(AdminStaffPermissions, ListView):
    model = Solicitudes
    paginate_by = 30
    template_name = 'admin/list_requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requests = Solicitudes.objects.all()
        context['total'] = requests
        context['validated'] = requests.filter(estatus='validated')
        context['direct_val'] = requests.filter(estatus='validated-direct')
        context['validated-direct'] = requests.filter(estatus='validated-direct')
        context['rejected'] = requests.filter(estatus='rejected')
        context['pending'] = requests.filter(estatus='pending')
        context['not_assign'] = requests.filter(estatus='')
        context['more3'] = requests.filter(mas_espacios=True)
        context['q'] = self.request.GET.get('q', '')
        context['e'] = self.request.GET.get('e', '')
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        e = self.request.GET.get('e', None)
        if q:
            lookup = (
                Q(pk__icontains=q) | Q(nombre__icontains=q) | Q(folio__icontains=q) |
                Q(comercio__nombre__icontains=q) | Q(usuario__first_name__icontains=q) |
                Q(usuario__last_name__icontains=q) | Q(usuario__email__icontains=q) |
                Q(usuario__phone_number__icontains=q) | Q(usuario__citas__folio=q) |
                Q(solicitud_lugar__folio__icontains=q)
            )

            queryset = queryset.filter(lookup)
            queryset = queryset.distinct("folio")
        if e:
            if e == 'noassign':
                queryset = queryset.filter(estatus='')
            elif e == 'more3':
                queryset = queryset.filter(mas_espacios=True)
            elif e in ['validated', 'rejected', 'resolved', 'pending', 'validated-direct']:
                queryset = queryset.filter(estatus=e)
        if not q:
            queryset = queryset.order_by('pk')

        return queryset

class ListUsers(AdminStaffPermissions, ListView):
    model = Usuarios
    paginate_by = 30
    template_name = 'admin/list_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = Usuarios.objects.all()
        context['total'] = users
        context['q'] = self.request.GET.get('q', '')
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        if q:
            lookup = (Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q)|Q(phone_number__icontains=q))
            queryset = queryset.filter(lookup)
        return queryset.order_by('pk')


class ListParking(AdminStaffPermissions, ListView):
    model = Estacionamiento
    paginate_by = 30
    template_name = 'admin/list_parking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarjetones = Estacionamiento.objects.all()
        context['total'] = tarjetones
        context['q'] = self.request.GET.get('q', '')
        context['form'] = ParkingForm()
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        if q:
            lookup = (Q(nombre__icontains=q)|Q(folio__icontains=q)|Q(placa__icontains=q))
            queryset = queryset.filter(lookup)
        return queryset.order_by('pk')
    
    def post(self, request, *args, **kwargs):
        form = ParkingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarjetón creado exitosamente')
        else:
            messages.error(request, 'Ha ocurrido un error al crear el Tarjetón')
            messages.error(request, form.errors)
        return redirect('admin:list_parking')


class ListDates(AdminStaffPermissions, ListView):
    model = CitasAgendadas
    paginate_by = 30
    template_name = 'admin/list_dates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = CitasAgendadas.objects.all()
        context['total'] = dates
        context['q'] = self.request.GET.get('q', '')
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        if q:
            lookup = (Q(folio__icontains=q)|Q(usuario__first_name__icontains=q)|Q(usuario__last_name__icontains=q)|Q(usuario__email__icontains=q))
            queryset = queryset.filter(lookup)
        return queryset.order_by('pk')


class UpdateRequest(AdminStaffPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_request.html'
    model = Solicitudes
    form_class = RequestForm
    success_message = 'Solicitud actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_request', kwargs={'uuid': self.object.uuid})


class UpdateShop(AdminStaffPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_shop.html'
    model = Comercios
    form_class = ShopForm
    success_message = 'Comercio actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_shop', kwargs={'uuid':self.object.uuid})


class UpdateUser(AdminStaffPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_user.html'
    model = Usuarios
    form_class = UserUpdateForm
    success_message = 'Usuario actualizado exitosamente'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_user', kwargs={'pk':self.object.pk})


class UpdateParking(AdminStaffPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_parking.html'
    model = Estacionamiento
    form_class = ParkingForm
    success_message = 'Tarjetón actualizado exitosamente'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_parking', kwargs={'pk':self.object.pk})


class Request(AdminStaffPermissions, DetailView):
    template_name = 'admin/request.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        request_ = self.get_object()
        if 'reverse-pay' in request.POST:
            if request_.estatus == 'validated':
                payment = request_.solicitud_pagos.first()
                if payment:
                    payment.delete()
                    Validaciones.objects.create(solicitud=request_, estatus=request_.estatus, atendido=True, comentarios='El validador revirtió la compra', validador=request.user.get_full_name())
                    messages.success(request, 'El pago se ha revertido exitosamente')
        if 'card-payment' in request.POST:
            if request_.estatus == 'validated':
                Pagos.objects.get_or_create(solicitud=request_, usuario=request_.usuario, tipo='tarjeta', pagado=True, validador=request.user.get_full_name())
                messages.success(request, 'El Pago se definió con tarjeta')
        elif 'cancel-pay' in request.POST:
            for place in request_.solicitud_lugar.all():
                for px in place.extras.all():
                    px.delete()
                place.delete()
            Validaciones.objects.create(solicitud=request_, estatus=request_.estatus, atendido=True, comentarios='El validador canceló la compra', validador=request.user.get_full_name())
            messages.success(request, 'El proceso de pago ha sido cancelado exitosamente')
        elif 'cash-payment' in request.POST:
            if request_.estatus == 'validated':
                Pagos.objects.get_or_create(solicitud=request_, usuario=request_.usuario, tipo='efectivo', pagado=False, validador=request.user.get_full_name())
                messages.success(request, 'El Pago se definió con efectivo. A la espera del comprobante del pago')
        elif 'cash-paid' in request.POST:
            if request_.estatus == 'validated':
                payment = request_.solicitud_pagos.first()
                if payment:
                    payment.pagado = True
                    payment.save()
                    messages.success(request, 'Se confirma el pago en efectivo')
        elif 'transfer-paid' in request.POST:
            if request_.estatus == 'validated-direct':
                place = Lugares.objects.get(uuid=request.POST.get('lugar'))
                place.precio = request.POST.get('monto')
                place.observacion = request.POST.get('descripcion')
                if request.FILES.get("factura"):
                    place.factura = request.FILES.get("factura")
                place.transfer_pago = True
                place.save()
                places = request_.solicitud_lugar.filter(estatus='assign')
                validados = places.filter(transfer_pago=True).count()
                total_tpay = places.count()

                if places.count() > 0 and validados == total_tpay:
                    if request_.estatus == 'validated' or request_.estatus == 'validated-direct':
                        if not Pagos.objects.filter(solicitud=request_):
                            Pagos.objects.get_or_create(
                                solicitud=request_, usuario=request_.usuario, tipo='transferencia', pagado=True,
                                validador=request_.usuario.get_full_name()
                            )
                messages.success(request, 'Se confirma para que el usuario pueda realizar los pagos')
        if 'validated' in request.POST:

            request_.estatus = 'validated'
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='validated', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
            send_html_mail(request_.usuario.email, request_.usuario.get_full_name, request_.folio, estatus='Aprobado')

        elif 'validated-payment' in request.POST:

            request_.estatus = 'validated-direct'
            request_.directo = True
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='validated-direct', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')

        elif 'rejected' in request.POST:
            reject_message = request.POST.get('reject-comments', 'Sin comentarios')
            request_.estatus = 'rejected'
            lookup = (~Q(estatus='rejected'))
            sib_req = Solicitudes.objects.filter(lookup, usuario=request_.usuario).exclude(uuid=request_.uuid)
            if not sib_req.exists():
                # quitar cita
                date = request_.usuario.citas.first()
                if date:
                    messages.warning(request, 'La Cita {} - {} fue liberada.'.format(date.fecha, date.hora))
                    date.delete()
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='rejected', validador=request.user.get_full_name(), comentarios=reject_message)
            messages.success(request, 'Estatus asignado exitosamente.')
            send_html_mail(request_.usuario.email, request_.usuario.get_full_name, request_.folio, estatus='Rechazado')
        elif 'pending' in request.POST:
            validation_fields = ['mas_espacios', 'factura', 'regimen_fiscal', 'nombre', 'nombre_replegal', 'rfc_txt', 'curp_txt', 'calle', 'no_calle', 'colonia', 'codigo_postal', 'estado', 'municipio', 'constancia_fiscal', 'comprobante_domicilio', 'acta_constitutiva', 'poder_notarial', 'identificacion', 'curp']
            data = {
                'just_fields': [],
                'field_comments': {}
            }
            for f in request.POST:
                if f in validation_fields:
                    if not request.POST.get(f).strip() == '':
                        data['just_fields'].append(f)
                        data['field_comments'][f] = request.POST.get(f).strip()
            if data['just_fields']:
                request_.estatus = 'pending'
                request_.save()
                Validaciones.objects.create(solicitud=request_, estatus='pending', validador=request.user.get_full_name(), campos=data)
                messages.success(request, 'Estatus asignado exitosamente.')
                send_html_mail(request_.usuario.email, request_.usuario.get_full_name, request_.folio, estatus='Pendiente de cambios')
            else:
                messages.warning(request, 'No se realizó ninguna acción. No se detectaron campos validados.')
        return redirect('admin:request', request_.uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # places = self.object.solicitud_lugar.filter(fecha_reg__year=2024, estatus='assign')
        places = self.object.solicitud_lugar.filter(estatus='assign')
        context['total_places'] = places.aggregate(price=Sum('precio'))['price'] or 0
        context['total_extras'] = places.aggregate(price=Sum('extras__precio'))['price'] or 0
        context['total'] = context['total_extras'] + context['total_places']
        context['selected_places'] = places
        context['tpay_places'] = places.exclude(data_tpay=None)
        context['history_places'] = HistorialTapy.objects.filter(lugar__in=places).order_by("-fecha_reg")
        context['payment'] = self.object.solicitud_pagos.first()
        pagado = False
        if self.object.estatus == "validated-direct" and self.object.solicitud_lugar.first():
            pagado = True
        if self.object.estatus == "validated" and self.object.solicitud_pagos.first():
            pagado = True
        context["pagado"] = pagado
        return context


class Shop(AdminStaffPermissions, DetailView):
    template_name = 'admin/shop.html'
    model = Comercios
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        shop_ = self.get_object()
        if 'validated' in request.POST:
            shop_.estatus = 'validated'
            shop_.save()
            Validaciones.objects.create(comercio=shop_, estatus='validated', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
            send_html_mail(shop_.solicitud.usuario.email, shop_.solicitud.usuario.get_full_name, shop_.folio, estatus='Aprobado')
        elif 'rejected' in request.POST:
            shop_.estatus = 'rejected'
            shop_.save()
            Validaciones.objects.create(comercio=shop_, estatus='rejected', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
            send_html_mail(shop_.solicitud.usuario.email, shop_.solicitud.usuario.get_full_name, shop_.folio, estatus='Rechazado')
        elif 'pending' in request.POST:
            validation_fields = ['giro', 'nombre', 'descripcion', 'imagen', 'vende_alcohol', 'voltaje', 'equipos']
            data = {
                'just_fields': [],
                'field_comments': {}
            }
            for f in request.POST:
                if f in validation_fields:
                    if not request.POST.get(f).strip() == '':
                        data['just_fields'].append(f)
                        data['field_comments'][f] = request.POST.get(f).strip()
            if data['just_fields']:
                shop_.estatus = 'pending'
                shop_.save()
                Validaciones.objects.create(comercio=shop_, estatus='pending', validador=request.user.get_full_name(), campos=data)
                messages.success(request, 'Estatus asignado exitosamente.')
                send_html_mail(shop_.solicitud.usuario.email, shop_.solicitud.usuario.get_full_name, shop_.folio, estatus='Pendiente de cambios')
            else:
                messages.warning(request, 'No se realizó ninguna acción. No se detectaron campos validados.')
        return redirect('admin:shop', shop_.uuid)


class SetPlace(AdminPermissions, TemplateView):
    template_name = 'admin/set_place.html'


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def render_place(request, key):
    for p in places_dict[key]['places']:
        if p['uuid']:
            p['status'] = 'available'
            if Lugares.objects.filter(uuid_place=p['uuid']).exists():
                p['status'] = 'unavailable'
    return JsonResponse(places_dict[key])


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def set_place_temp(request, uuid, zone):
    places = request.POST.getlist('places')
    request_ = Solicitudes.objects.get(uuid=uuid)
    objects = []
    if zone in ['n_1', 'n_2', 'n_3', 'z_a', 'z_b', 'z_c', 'z_d', 's_t', 'teatro']:
        for p in places:
            for p2 in places_dict[zone]['places']:
                if p2['uuid'] == str(p):
                    objects.append(Lugares(uuid_place=p, tramite_id=p2["concept"], solicitud=request_, usuario=request_.usuario, estatus='temp', zona=zone, precio=p2['price'], m2=p2['m2'], nombre=p2['text']))
        try:
            obj = Lugares.objects.bulk_create(objects)
            for o in obj:
                o.save()
            return Response({'status_code': 'saved'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status_code': 'notsaved', 'error': str(e)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def unset_place_temp(request, uuid):
    places = request.POST.getlist('places')
    for p in places:
        p_ = Lugares.objects.filter(uuid_place=p, estatus='temp')
        if p_.exists():
            p_.get().delete()
    return Response({})


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def set_place(request, uuid):
    places = request.POST.getlist('places')
    for p in places:
        p_ = Lugares.objects.filter(uuid_place=p)
        if p_.exists():
            pl = p_.get()
            pl.estatus = 'assign'
            pl.save()
    return Response({})


class DownloadDateDoc(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            date = CitasAgendadas.objects.get(uuid=kwargs['uuid_date'])
            doc = get_date_constancy(request_, date)
            return doc
        except (Solicitudes.DoesNotExist, CitasAgendadas.DoesNotExist):
            raise Http404()


class DownloadContract(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            doc = generate_physical_document(request_)
            return doc
        except (Solicitudes.DoesNotExist):
            raise Http404()


class DownloadGafete(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            place = Lugares.objects.get(uuid=kwargs['uuid_place'])
            gafete = get_gafete(place)
            return gafete
        except (Solicitudes.DoesNotExist, Lugares.DoesNotExist):
            raise Http404()


class DownloadSuministros(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            place = Lugares.objects.get(uuid=kwargs['uuid_place'])
            gafete = get_suministros(place)
            return gafete
        except (Solicitudes.DoesNotExist, Lugares.DoesNotExist):
            raise Http404()


class DownloadTarjeton(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            tarjeton = Estacionamiento.objects.get(uuid=kwargs['uuid'])
            doc = get_tarjeton(tarjeton)
            return doc
        except (Estacionamiento.DoesNotExist):
            raise Http404()


class DownloadReport(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            report = get_report()
            return report
        except Exception as e:
            print(e)
            return redirect('admin:main')


class DownloadRequestsReport(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            report = get_requests_report()
            return report
        except Exception as e:
            print(e)
            return redirect('admin:main')

class DownloadStandsReport(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            report = get_stands_report(places_dict)
            return report
        except Exception as e:
            print(e)
            return redirect('admin:main')

class DownloadReceipt(AdminStaffPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            place = Lugares.objects.get(uuid=kwargs['uuid_place'])
            receipt = get_receipt(place)
            return receipt
        except (Solicitudes.DoesNotExist, Lugares.DoesNotExist):
            raise Http404()


class UnlockRequest(AdminStaffPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            validation = request_.get_last_unattended_validation()
            if validation:
                validation.atendido = True
                validation.save()
            request_.estatus = ''
            request_.save()
            Validaciones.objects.create(solicitud=request_, comentarios='Validación desbloqueada por el validador', estatus='pending', atendido=True, validador=request.user.get_full_name())
            messages.success(request, 'Validación Desbloqueada')
            return redirect('admin:request', request_.uuid)
        except (Solicitudes.DoesNotExist):
            raise Http404()


class UserDates(AdminStaffPermissions, TemplateView):
    template_name = 'admin/user_dates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.user = Usuarios.objects.get(pk__exact=self.kwargs['pk'])
        except Usuarios.DoesNotExist:
            raise Http404()
        context['user'] = self.user
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        date = request.POST.get('date')
        time = request.POST.get('time')
        scheduled = CitasAgendadas.objects.filter(fecha=date, hora=time)
        if scheduled.count() < settings.ATTENTION_MODULES:
            CitasAgendadas.objects.create(fecha=date, hora=time, usuario=self.user)
            messages.success(request, 'Cita agendada exitosamente.')
            return redirect('admin:list_users')
        return self.render_to_response(context)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def add_terraza(request, uuid, uuid_place):
    terraza_price = 4500
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=request.POST.get('terraza'))
        ProductosExtras.objects.create(lugar=place, tipo='terraza', precio=terraza_price, m2=9, to_places=place.folio)
        return Response({})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def add_descuento(request, uuid, uuid_place):
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=request.POST.get('terraza'))
        if place.tramite_id:
            place.precio = Decimal(place_concept_des[place.tramite_id.__str__()][1])
            place.tramite_id = place_concept_des[place.tramite_id.__str__()][0]
            place.tpay_descuento = True
            place.save()
        return Response({})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def add_big_terraza(request, uuid, uuid_place):
    terraza_price = 8000
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=request.POST.get('terraza_grande'))
        ProductosExtras.objects.create(lugar=place, tipo='terraza_grande', precio=terraza_price, m2=9, to_places=place.folio)
        return Response({})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def add_alcohol(request, uuid, uuid_place):
    alcohol_price = 0
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        places = Lugares.objects.filter(uuid__in=request.POST.getlist('alcohol'))
        mt2 = places.aggregate(m2=Sum('m2'))['m2'] or 0
        if mt2<=50:
            alcohol_price = 34742.40
        elif mt2>50 and mt2<=100:
            alcohol_price = 69478.40
        elif mt2>100 and mt2<=150:
            alcohol_price = 121598.40
        elif mt2 > 150:
            alcohol_price = 260568
        if places:
            to_places = ''
            place = False
            # ProductosExtras.objects.create(lugar=places[0], tipo='licencia_alcohol', precio=alcohol_price, m2=mt2, to_places=to_places)
            for p in places:
                to_places = "{}{},".format(to_places, p.folio)
                if place_concept_alcohol[p.tramite_id.__str__()][0] != 0:
                    ProductosExtras.objects.create(
                        lugar=p, tipo='licencia_alcohol', m2=p.m2, to_places=p.folio,
                        precio_tpay=p.precio, tramite_id=p.tramite_id
                    )
                    p.precio = Decimal(place_concept_alcohol[p.tramite_id.__str__()][1])
                    p.tramite_id = place_concept_alcohol[p.tramite_id.__str__()][0]
                    p.tpay_alcohol = True
                    p.save()
                    place = True
            return Response({"proceso": place})
        else:
            return Response({'message': 'not-places-existing', "proceso": False})
    except Exception as e:
        return Response({'message': str(e), "proceso": False}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def delete_item(request, uuid, uuid_pdt):
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        pdt = ProductosExtras.objects.get(uuid=request.POST.get('item'))
        if pdt.tipo == 'licencia_alcohol':
            place = pdt.lugar
            place.tramite_id = pdt.tramite_id
            place.precio = pdt.precio_tpay
            place.save()
        pdt.delete()
        Validaciones.objects.create(solicitud=request_, estatus=request_.estatus, atendido=True, comentarios='El validador eliminó un producto de la compra', validador=request.user.get_full_name())
        return Response({})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def delete_place(request, uuid, uuid_place):
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=request.POST.get('place'))
        if not place.data_tpay:
            HistorialTapy.objects.filter(lugar=place).delete()
            place.delete()

            Validaciones.objects.create(solicitud=request_, estatus=request_.estatus, atendido=True, comentarios='El validador eliminó un espacio de la compra', validador=request.user.get_full_name())
            return Response({"eliminado": True})

        return Response({"eliminado": False})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def aplicar_pago_caja(request, uuid, uuid_place):
    try:
        registro = False
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=uuid_place)
        place.caja_folio = request.POST.get('folio')
        place.caja_pago = True
        place.save()
        places = request_.solicitud_lugar.filter(estatus='assign')
        validados = places.filter(caja_pago=True).count()
        total_tpay = places.count()

        if places.count() > 0 and validados == total_tpay:
            if request_.estatus == 'validated' or request_.estatus == 'validated-direct':
                if not Pagos.objects.filter(solicitud=request_):
                    Pagos.objects.get_or_create(
                        solicitud=request_, usuario=request_.usuario, tipo='caja', pagado=True,
                        validador=request_.usuario.get_full_name()
                    )
        return Response({"proceso": True})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def aplicar_pago_transfer(request, uuid, uuid_place):
    try:
        registro = False
        request_ = Solicitudes.objects.get(uuid=uuid)
        place = Lugares.objects.get(uuid=uuid_place)
        place.precio = request.POST.get('monto')
        place.transfer_pago = True
        place.save()
        places = request_.solicitud_lugar.filter(estatus='assign')
        validados = places.filter(transfer_pago=True).count()
        total_tpay = places.count()

        if places.count() > 0 and validados == total_tpay:
            if request_.estatus == 'validated' or request_.estatus == 'validated-direct':
                if not Pagos.objects.filter(solicitud=request_):
                    Pagos.objects.get_or_create(
                        solicitud=request_, usuario=request_.usuario, tipo='transferencia', pagado=True,
                        validador=request_.usuario.get_full_name()
                    )
        return Response({"proceso": True})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistroManualUbicacion(AdminStaffPermissions, DetailView):
    template_name = 'admin/ubicacion_manual.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        request_ = self.get_object()

        if request_.comercio.giro == 'ambulante':
            comercio = request_.comercio
            comercio.subgiro = self.request.POST.get("subgiro")
            nombre = Lugares.objects.filter(estatus='assign', zona='amb').count() + 1
            Lugares.objects.create(
                estatus='assign', zona='amb',
                nombre=nombre.__str__(),
                usuario=request_.usuario, solicitud=request_,
                precio=Decimal(ambulante_concept[self.request.POST.get("subgiro")][1]),
                tramite_id=ambulante_concept[self.request.POST.get("subgiro")][0], uuid_place=str(uuid.uuid4()),
                observacion=self.request.POST.get("observacion")
            )
            comercio.save()
            messages.success(request, 'La ubicación ha sido asingada a la solicitud')

        else:
            lugar = Lugares.objects.filter(
                zona=self.request.POST.get("zona"), nombre=self.request.POST.get("nombre")
            ).first()
            if not lugar:
                # uuid_place = None
                # for p2 in places_dict[self.request.POST.get("zona")]['places']:
                #     if int(p2['text']) == int(request.POST.get("nombre")):
                #         uuid_place = p2["uuid"]
                # if uuid_place:
                Lugares.objects.create(
                    estatus='assign', zona=self.request.POST.get("zona"),
                    nombre=self.request.POST.get("nombre"),
                    usuario=request_.usuario, solicitud=request_, m2=self.request.POST.get("m2"),
                    precio=self.request.POST.get("precio"), uuid_place=str(uuid.uuid4()),
                    observacion=self.request.POST.get("observacion")
                )
                messages.success(request, 'La ubicación ha sido asingada a la solicitud')
                # else:
                #     messages.warning(request, 'La ubicación no se encuentra mapeada.')
            else:
                messages.warning(request, 'La ubicación ya ha sido asingada a otro usuario.')
        return redirect('admin:request', request_.uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # places = self.object.solicitud_lugar.filter(fecha_reg__year=2024, estatus='assign')pagado
        context["zonas_list"] = [
            ('z_a', 'Zona A'), ('z_b', 'Zona B'), ('z_c', 'Zona C'), ('z_d', 'Zona D'), ('n_1', 'Nave 1'),
            ('n_2', 'Nave 2'), ('n_3', 'Nave 3'), ('s_t', 'Sabor a Tab.'), ('teatro', 'Teatro al A. L.'),
            ('patrocinador', 'Patrocinador'), ('ganadera', 'Ganadera'), ('flor', 'Elección Flor')
        ]
        context["subgiro_list"] = (
            ('amb_1', 'Chicharrones y otros'),
            # ('amb_2', 'Cigarros y otros'),
            ('amb_3', 'Esquites, aguas'),
        )
        return context