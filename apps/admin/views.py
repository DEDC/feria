# Django
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
# places
from apps.places.models import Solicitudes, Comercios, Validaciones, Lugares, ProductosExtras, Pagos
from apps.places.forms import RequestForm, ShopForm
# users
from apps.users.models import Usuarios
from apps.users.forms import UserUpdateForm
# dates
from apps.dates.models import CitasAgendadas
# utils
from utils.naves import nave1, nave3, zona_a, zona_b, zona_c, zona_d
from utils.permissions import AdminPermissions
from utils.date import get_date_constancy
from utils.gafete import get_gafete
from utils.word_writer import generate_physical_document

places_dict = {'n_1': nave1, 'n_3': nave3, 'z_a': zona_a, 'z_b': zona_b, 'z_c': zona_c, 'z_d': zona_d}

class Main(AdminPermissions, TemplateView):
    template_name = 'admin/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = Solicitudes.objects.all().order_by('fecha_reg')
        context['dates'] = CitasAgendadas.objects.all().order_by('fecha', 'hora')
        context['branches'] = Comercios.objects.all().order_by('nombre')
        return context

class ListRequests(AdminPermissions, ListView):
    model = Solicitudes
    paginate_by = 30
    template_name = 'admin/list_requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requests = Solicitudes.objects.all()
        context['total'] = requests
        context['validated'] = requests.filter(estatus='validated')
        context['rejected'] = requests.filter(estatus='rejected')
        context['pending'] = requests.filter(estatus='pending')
        context['not_assign'] = requests.filter(estatus='')
        context['q'] = self.request.GET.get('q', '')
        context['e'] = self.request.GET.get('e', '')
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        e = self.request.GET.get('e', None)
        if q:
            lookup = (Q(pk__icontains=q)|Q(nombre__icontains=q)|Q(folio__icontains=q)|
                      Q(comercio__nombre__icontains=q)|Q(usuario__first_name__icontains=q)|
                      Q(usuario__last_name__icontains=q)|Q(usuario__email__icontains=q)|
                      Q(usuario__phone_number__icontains=q)|Q(usuario__citas__folio=q))
            queryset = queryset.filter(lookup)
        if e:
            if e == 'noassign':
                queryset = queryset.filter(estatus='')
            elif e in ['validated', 'rejected', 'resolved', 'pending']:
                queryset = queryset.filter(estatus=e)
        return queryset.order_by('pk')

class ListUsers(AdminPermissions, ListView):
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

class ListDates(AdminPermissions, ListView):
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

class UpdateRequest(AdminPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_request.html'
    model = Solicitudes
    form_class = RequestForm
    success_message = 'Solicitud actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_request', kwargs={'uuid':self.object.uuid})

class UpdateShop(AdminPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_shop.html'
    model = Comercios
    form_class = ShopForm
    success_message = 'Comercio actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_shop', kwargs={'uuid':self.object.uuid})

class UpdateUser(AdminPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_user.html'
    model = Usuarios
    form_class = UserUpdateForm
    success_message = 'Usuario actualizado exitosamente'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_user', kwargs={'pk':self.object.pk})

class Request(AdminPermissions, DetailView):
    template_name = 'admin/request.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        request_ = self.get_object()
        if 'card-payment' in request.POST:
            if request_.estatus == 'validated':
                Pagos.objects.get_or_create(solicitud=request_, usuario=request_.usuario, tipo='tarjeta', pagado=True)
                messages.success(request, 'El Pago se definió con tarjeta')
        elif 'cancel-pay' in request.POST:
            for place in request_.solicitud_lugar.all():
                for px in place.extras.all():
                    px.delete()
                place.delete()
            messages.success(request, 'El proceso de pago ha sido cancelado exitosamente')
        elif 'cash-payment' in request.POST:
            if request_.estatus == 'validated':
                Pagos.objects.get_or_create(solicitud=request_, usuario=request_.usuario, tipo='efectivo', pagado=False)
                messages.success(request, 'El Pago se definió con efectivo. A la espera del comprobante del pago')
        elif 'cash-paid' in request.POST:
            if request_.estatus == 'validated':
                payment = request_.solicitud_pagos.first()
                if payment:
                    payment.pagado = True
                    payment.save()
                    messages.success(request, 'Se confirma el pago en efectivo')

        if 'validated' in request.POST:
            request_.estatus = 'validated'
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='validated', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'rejected' in request.POST:
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
            Validaciones.objects.create(solicitud=request_, estatus='rejected', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'pending' in request.POST:
            validation_fields = ['factura', 'regimen_fiscal', 'nombre', 'nombre_replegal', 'rfc_txt', 'curp_txt', 'calle', 'no_calle', 'colonia', 'codigo_postal', 'estado', 'municipio', 'constancia_fiscal', 'comprobante_domicilio', 'acta_constitutiva', 'identificacion', 'curp']
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
            else:
                messages.warning(request, 'No se realizó ninguna acción. No se detectaron campos validados.')
        return redirect('admin:request', request_.uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        places = self.object.solicitud_lugar.filter(fecha_reg__year=2024, estatus='assign')
        context['total_places'] = places.aggregate(price=Sum('precio'))['price'] or 0
        context['total_extras'] = places.aggregate(price=Sum('extras__precio'))['price'] or 0
        context['total'] = context['total_extras'] + context['total_places']
        context['selected_places'] = places
        context['payment'] = self.object.solicitud_pagos.first()
        return context

class Shop(AdminPermissions, DetailView):
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
        elif 'rejected' in request.POST:
            shop_.estatus = 'rejected'
            shop_.save()
            Validaciones.objects.create(comercio=shop_, estatus='rejected', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'pending' in request.POST:
            validation_fields = ['nombre', 'descripcion', 'imagen', 'vende_alcohol', 'voltaje', 'equipos']
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
    if zone in ['z_a', 'z_b', 'z_c', 'z_d', 'n_1', 'n_3']:
        for p in places:
            for p2 in places_dict[zone]['places']:
                if p2['uuid'] == str(p):
                    objects.append(Lugares(uuid_place=p, solicitud=request_, usuario=request_.usuario, estatus='temp', zona=zone, precio=p2['price'], m2=p2['m2'], nombre=p2['text']))
        try:
            obj = Lugares.objects.bulk_create(objects)
            for o in obj:
                o.save()
            return Response({'status_code': 'saved'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'status_code': 'notsaved'}, status=status.HTTP_200_OK)

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

class DownloadGafate(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            place = Lugares.objects.get(uuid=kwargs['uuid_place'])
            gafete = get_gafete(place)
            return gafete
        except (Solicitudes.DoesNotExist, Lugares.DoesNotExist):
            raise Http404()

class UnlockRequest(AdminPermissions, RedirectView):
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

class UserDates(AdminPermissions, TemplateView):
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
def delete_item(request, uuid, uuid_place):
    try:
        request_ = Solicitudes.objects.get(uuid=uuid)
        pdt = ProductosExtras.objects.get(uuid=request.POST.get('terraza'))
        pdt.delete()
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

# delete items here

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
            alcohol_price = 69484.80
        elif mt2>100 and mt2<=150:
            alcohol_price = 121598.40
        elif mt2 > 150:
            alcohol_price = 260568
        if places:
            to_places = ','.join(places.values_list('folio', flat=True))
            ProductosExtras.objects.create(lugar=places[0], tipo='licencia_alcohol', precio=alcohol_price, m2=100, to_places=to_places)
            return Response({})
        else:
            return Response({'message': 'not-places-existing'})
    except Exception as e:
        return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)