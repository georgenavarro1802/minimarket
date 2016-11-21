#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from store.forms import SesionCajaForm, CierreSesionCajaForm
from store.functions import salva_auditoria, MiPaginador, bad_json, ok_json, url_back, mensaje_excepcion
from store.models import SesionCaja, CierreSesionCaja
from store.values import ACCION_ADICIONAR, ACCION_MODIFICAR
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Cash Register Sessions'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'abrirsesion':
            f = SesionCajaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sc = SesionCaja(fondo=f.cleaned_data['fondo'],
                                        fecha=datetime.now(),
                                        facturaempieza=f.cleaned_data['facturaempieza'],
                                        facturatermina=f.cleaned_data['facturaempieza'],
                                        abierta=True,
                                        cajero=f.cleaned_data['cajero'])
                        sc.save()
                        salva_auditoria(request, sc, ACCION_ADICIONAR)
                        return ok_json()
                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'cerrarsesion':
            sesion = SesionCaja.objects.get(pk=request.POST['id'])
            f = CierreSesionCajaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        closed_session = CierreSesionCaja(sesion=sesion,
                                                          bill100=f.cleaned_data['bill100'],
                                                          bill50=f.cleaned_data['bill50'],
                                                          bill20=f.cleaned_data['bill20'],
                                                          bill10=f.cleaned_data['bill10'],
                                                          bill5=f.cleaned_data['bill5'],
                                                          bill2=f.cleaned_data['bill2'],
                                                          bill1=f.cleaned_data['bill1'],
                                                          total=0,
                                                          enmonedas=f.cleaned_data['enmonedas'],
                                                          deposito=f.cleaned_data['deposito'])
                        closed_session.save()
                        sesion.abierta = False
                        sesion.save()
                        salva_auditoria(request, closed_session, ACCION_MODIFICAR)
                        return ok_json()
                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'addsesion':
                try:
                    data['title'] = 'Open Cash Register Session'
                    data['form'] = SesionCajaForm()
                    return render_to_response("caja/adicionarbs.html", data)
                except Exception:
                    pass

            elif action == 'closesesion':
                try:
                    data['title'] = 'Close Cash Register Session'
                    data['sesioncaja'] = SesionCaja.objects.get(pk=request.GET['id'])
                    data['form'] = CierreSesionCajaForm()
                    return render_to_response("caja/cerrarsesionbs.html", data)
                except Exception:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        sesiones = SesionCaja.objects.all()
        paging = MiPaginador(sesiones, 25)
        p = 1
        try:
            if 'page' in request.GET:
                p = int(request.GET['page'])
            page = paging.page(p)
        except:
            page = paging.page(1)
        data['paging'] = paging
        data['rangospaging'] = paging.rangos_paginado(p)
        data['page'] = page
        data['sesiones'] = page.object_list
        data['exists_open_sessions'] = SesionCaja.objects.filter(abierta=True).exists()
        return render_to_response("caja/sesionesbs.html", data)
