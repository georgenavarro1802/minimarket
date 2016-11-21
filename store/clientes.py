#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from store.forms import ClienteForm
from store.functions import model_to_dict_safe, bad_json, url_back, mensaje_excepcion, MiPaginador, salva_auditoria, \
    ok_json
from store.models import Cliente
from store.values import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Customers'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ClienteForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        ruc = f.cleaned_data['ruc']
                        if not Cliente.objects.filter(ruc=ruc).exists():
                            cliente = Cliente(ruc=f.cleaned_data['ruc'],
                                              nombre=f.cleaned_data['nombre'],
                                              direccion=f.cleaned_data['direccion'],
                                              email=f.cleaned_data['email'],
                                              telefono=f.cleaned_data['telefono'])
                            cliente.save()
                            salva_auditoria(request, cliente, ACCION_ADICIONAR)
                            return ok_json()
                        else:
                            return bad_json(mensaje='Identification already exists')
                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            cliente = Cliente.objects.get(pk=request.POST['id'])
            f = ClienteForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        ruc = f.cleaned_data['ruc']
                        if not Cliente.objects.filter(ruc=ruc).exclude(id=cliente.id).exists():
                            cliente.ruc = f.cleaned_data['ruc']
                            cliente.nombre = f.cleaned_data['nombre']
                            cliente.direccion = f.cleaned_data['direccion']
                            cliente.email = f.cleaned_data['email']
                            cliente.telefono = f.cleaned_data['telefono']
                            cliente.save()
                            salva_auditoria(request, cliente, ACCION_MODIFICAR)
                            return ok_json()
                        else:
                            return bad_json(mensaje='Identification already exists')
                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            try:
                with transaction.atomic():
                    cliente = Cliente.objects.get(pk=request.POST['id'])
                    salva_auditoria(request, cliente, ACCION_ELIMINAR)
                    cliente.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = 'Add Customer'
                    data['form'] = ClienteForm()
                    return render_to_response("clientes/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = 'Edit Customer'
                    data['cliente'] = cliente = Cliente.objects.get(pk=request.GET['id'])
                    initial = model_to_dict_safe(cliente)
                    data['form'] = ClienteForm(initial=initial)
                    return render_to_response("clientes/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = 'Delete Customer'
                    data['cliente'] = Cliente.objects.get(pk=request.GET['id'])
                    return render_to_response("clientes/delete.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))
        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']
            if search:
                clientes = Cliente.objects.filter(Q(nombre__icontains=search) | Q(identificacion__icontains=search))
            else:
                clientes = Cliente.objects.all()

            paging = MiPaginador(clientes, 25)
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
            data['search'] = search if search else ""
            data['clientes'] = page.object_list
            return render_to_response("clientes/clientes.html", data)
