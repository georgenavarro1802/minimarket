#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from store.models import SesionCaja, TipoProducto
from store.functions import (convertir_fecha, addUserData, total_pagos_rango_fechas, total_ingreso_tipo,
                             total_columnas, pagos_total_fecha, pagos_total_fecha_credito,
                             pagos_total_fecha_credito_sesion, total_efectivo_dia)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': 'Stats and Charts'}
    addUserData(request, data)
    data['hoy'] = hoy = datetime.now().date()
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'char_menu1':
            data = {"results": [{"id": x.id, "cajero": x.cajero} for x in SesionCaja.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month, fecha__day=hoy.day)]}
            return HttpResponse(json.dumps(data), content_type='application/json')

        elif action == 'colchartsesionfecha':
            fecha = convertir_fecha(request.POST['fecha'])
            data = {"results": [{"id": x.id, "cajero": x.cajero} for x in SesionCaja.objects.filter(fecha=fecha)]}
            return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        # tbl-dia
        if SesionCaja.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month, fecha__day=hoy.day).exists():
            data['sesioncaja_dia'] = SesionCaja.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month, fecha__day=hoy.day)[0]
        else:
            data['sesioncaja_dia'] = None

        return render_to_response("estadisticas/estadisticas.html", data)
