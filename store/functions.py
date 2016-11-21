#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
from decimal import Decimal

import requests
from django.contrib.admin.models import CHANGE, ADDITION, DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Sum
from django.forms import model_to_dict
from django.http import HttpResponse

from store.models import Venta
from store.values import FACTURACION_API_URL, ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR

NOMBRE_INSTITUCION = 'MINIMARKET DEMO'

DEFAULT_PASSWORD = 'assets'

MENSAJES_ERROR = [
    u'Permiso denegado.',
    u'No tiene permiso para modificar la inscripcion.',
    u'No tiene permiso para realizar esta accion.'
]


def addUserData(request, data):
    data['usuario'] = request.user
    data['currenttime'] = datetime.now()
    data['nombreinstitucion'] = NOMBRE_INSTITUCION


def generate_file_name(nombre, original):
    ext = ""
    if original.find(".") > 0:
        ext = original[original.rfind("."):]
    fecha = datetime.now().date()
    hora = datetime.now().time()
    return nombre + fecha.year.__str__() + fecha.month.__str__() + fecha.day.__str__() + \
           hora.hour.__str__() + hora.minute.__str__() + hora.second.__str__() + ext


class MiPaginador(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(MiPaginador, self).__init__(object_list, per_page, orphans=orphans,
                                          allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left < 1:
            left = 1
        if right > self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right + 1)
        self.primera_pagina = True if left > 1 else False
        self.ultima_pagina = True if right < self.num_pages else False
        self.ellipsis_izquierda = left - 1
        self.ellipsis_derecha = right + 1


def convertir_fecha(s):
    try:
        return datetime(int(s[-4:]), int(s[3:5]), int(s[:2]))
    except:
        return datetime.now()


def model_to_dict_safe(m, exclude=None):
    if not exclude:
        exclude = []
    d = model_to_dict(m, exclude=exclude)
    for x, y in d.iteritems():
        if type(y) == Decimal:
            d[x] = float(y)
    return d


def url_back(request, mensaje=None):
    url = request.META['HTTP_REFERER'].split('/')[-1:][0]
    if 'mensj=' in url:
        url = url[:(url.find('mensj') - 1)]
    if mensaje:
        if '?' in url:
            url += "&mensj=" + mensaje
        else:
            url += "?mensj=" + mensaje
    return url


def mensaje_excepcion(mensaje):
    if mensaje not in MENSAJES_ERROR:
        mensaje = MENSAJES_ERROR[0]
    return mensaje


def bad_json(mensaje=None, error=None, extradata=None):
    data = {'result': 'bad'}
    if mensaje:
        data.update({'mensaje': mensaje})
    if error:
        if error == 0:
            data.update({"mensaje": "Incorrect request"})
        elif error == 1:
            data.update({"mensaje": "Error saving data"})
        elif error == 2:
            data.update({"mensaje": "Error modifying data"})
        elif error == 3:
            data.update({"mensaje": "Error deleting data"})
        elif error == 4:
            data.update({"mensaje": "You dont have permission to perform this action"})
        elif error == 5:
            data.update({"mensaje": "Error generating the information"})
        else:
            data.update({"mensaje": "System error"})
    if extradata:
        data.update(extradata)
    return HttpResponse(json.dumps(data), content_type="application/json")


def ok_json(data=None, simple=None):
    if data:
        if not simple:
            if 'result' not in data.keys():
                data.update({"result": "ok"})
    else:
        data = {"result": "ok"}
    return HttpResponse(json.dumps(data), content_type="application/json")


def obtener_ip(request):
    try:
        client_address = request.META['HTTP_X_FORWARDED_FOR']  # server externo
    except:
        client_address = request.META['REMOTE_ADDR']  # localhost
    return client_address


# Metodo para Salvas en Tablas Auditoras - (Django LogEntry y en AudiUsuarioTabla)
def salva_auditoria(request, model, action, mensaje=''):
    # Obtain client ip address
    client_address = obtener_ip(request)

    flagEntry = CHANGE
    # Elegir Tipo de Accion - Asignar Django LogEntry Action y Message correspondiente
    if action == ACCION_ADICIONAR:
        flagEntry = ADDITION
        flagMessage = 'Adicionado ' + model.__class__.__name__ + ' (' + client_address + ')'
    elif action == ACCION_MODIFICAR:
        flagEntry = CHANGE
        flagMessage = 'Modificado ' + model.__class__.__name__ + ' (' + client_address + ')'
    elif action == ACCION_ELIMINAR:
        flagEntry = DELETION
        flagMessage = 'Eliminado ' + model.__class__.__name__ + ' (' + client_address + ')'
    else:
        flagMessage = mensaje + ' (' + client_address + ')'

    # Registro en Django LogEntry
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=model.id,
        object_repr=model.__str__(),
        action_flag=flagEntry,
        change_message=flagMessage
    )


# Stats functions
def cantidad_facturas_anuladas(month, year):
    datos = requests.get(FACTURACION_API_URL, params={'a': 'facturasanuladas', 'month': month, 'year': year})
    if datos.status_code == 200:
        return len(datos.json())
    return 0


def total_efectivo_dia(fecha):
    if Venta.objects.filter(sesioncaja__fecha=fecha, valida=True).exists():
        return Venta.objects.filter(sesioncaja__fecha=fecha, valida=True).aggregate(Sum('total'))['total__sum']
    return 0


def total_pagos_rango_fechas(inicio, fin):
    if Venta.objects.filter(sesioncaja__fecha__gte=inicio, sesioncaja__fecha__lte=fin).exists():
        return Decimal(
            Venta.objects.filter(sesioncaja__fecha__gte=inicio, sesioncaja__fecha__lte=fin).aggregate(Sum('total'))[
                'total__sum'])
    return 0


def total_ingreso_tipo(fecha, tipo):
    if Venta.objects.filter(sesioncaja__fecha=fecha, detalles__producto__tipoproducto=tipo).exists():
        return \
        Venta.objects.filter(sesioncaja__fecha=fecha, detalles__producto__tipoproducto=tipo).aggregate(Sum('total'))[
            'total__sum']
    return 0


def total_columnas(inicio, fin, tipo):
    if Venta.objects.filter(sesioncaja__fecha__gte=inicio, sesioncaja__fecha__lte=fin,
                            detalles__producto__tipoproducto=tipo).exists():
        return Venta.objects.filter(sesioncaja__fecha__gte=inicio, sesioncaja__fecha__lte=fin,
                                    detalles__producto__tipoproducto=tipo).aggregate(Sum('total'))['total__sum']
    return 0


def total_dia(fecha):
    return total_efectivo_dia(fecha)


def pagos_total_fecha(fecha):
    if Venta.objects.filter(sesioncaja__fecha=fecha, valida=True).exists():
        return Venta.objects.filter(sesioncaja__fecha=fecha, valida=True).aggregate(Sum('total'))['total__sum']
    return 0


def pagos_total_fecha_credito(fecha):
    return 0
    # return Venta.objects.filter(sesioncaja__fecha=fecha, valida=True).exclude(
    #     Q(cliente__tipo__id=CLIENTES_EXTERNOS_ID) | Q(cliente__tipo__id=CONSUMIDOR_FINAL_ID)).aggregate(Sum('total'))[
    #     'total__sum'] if Venta.objects.filter(sesioncaja__fecha=fecha, sesioncaja__caja__cafeteria=cafeteria).exclude(
    #     Q(cliente__tipo__id=CLIENTES_EXTERNOS_ID) | Q(cliente__tipo__id=CONSUMIDOR_FINAL_ID)).exists() else 0


def pagos_total_fecha_credito_sesion(sesion):
    return 0
    # return Decimal(Venta.objects.filter(sesioncaja=sesion, valida=True).exclude(
    #     Q(cliente__tipo__id=CLIENTES_EXTERNOS_ID) | Q(cliente__tipo__id=CONSUMIDOR_FINAL_ID)).aggregate(Sum('total'))[
    #                    'total__sum']) if Venta.objects.filter(sesioncaja=sesion, valida=True).exclude(
    #     Q(cliente__tipo__id=CLIENTES_EXTERNOS_ID) | Q(cliente__tipo__id=CONSUMIDOR_FINAL_ID)).exists() else 0
