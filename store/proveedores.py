#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from store.forms import ProveedorForm
from store.functions import (model_to_dict_safe, bad_json, url_back, mensaje_excepcion, MiPaginador,
                             salva_auditoria, ok_json)
from store.models import Proveedor
from store.values import ACCION_ADICIONAR
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Suppliers'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ProveedorForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        identificacion = f.cleaned_data['identificacion']
                        if not Proveedor.objects.filter(identificacion=identificacion).exists():
                            proveedor = Proveedor(identificacion=f.cleaned_data['identificacion'],
                                                  nombre=f.cleaned_data['nombre'],
                                                  alias=f.cleaned_data['alias'],
                                                  direccion=f.cleaned_data['direccion'],
                                                  telefono=f.cleaned_data['telefono'],
                                                  celular=f.cleaned_data['celular'],
                                                  email=f.cleaned_data['email'])
                            proveedor.save()
                            salva_auditoria(request, proveedor, ACCION_ADICIONAR)
                            return ok_json()
                        else:
                            return bad_json(mensaje='Identification already exists')
                except Exception:
                    return bad_json(error=1)

        elif action == 'edit':
            proveedor = Proveedor.objects.get(pk=request.POST['id'])
            f = ProveedorForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        identificacion = f.cleaned_data['identificacion']
                        if not Proveedor.objects.filter(identificacion=identificacion).exclude(id=proveedor.id).exists():
                            proveedor.identificacion = f.cleaned_data['identificacion']
                            proveedor.nombre = f.cleaned_data['nombre']
                            proveedor.alias = f.cleaned_data['alias']
                            proveedor.direccion = f.cleaned_data['direccion']
                            proveedor.telefono = f.cleaned_data['telefono']
                            proveedor.celular = f.cleaned_data['celular']
                            proveedor.email = f.cleaned_data['email']
                            proveedor.save()
                            salva_auditoria(request, proveedor, ACCION_ADICIONAR)
                            return ok_json()
                        else:
                            return bad_json(mensaje='Identification already exists')
                except Exception:
                    return bad_json(error=2)

        elif action == 'delete':
            proveedor = Proveedor.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    proveedor.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = 'Add Supplier'
                    data['form'] = ProveedorForm()
                    return render_to_response("proveedores/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = 'Edit Supplier'
                    data['proveedor'] = proveedor = Proveedor.objects.get(pk=request.GET['id'])
                    initial = model_to_dict_safe(proveedor)
                    data['form'] = ProveedorForm(initial=initial)
                    return render_to_response("proveedores/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = 'Delete Supplier'
                    data['proveedor'] = Proveedor.objects.get(pk=request.GET['id'])
                    return render_to_response("proveedores/delete.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))
        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']
            if search:
                proveedores = Proveedor.objects.filter(Q(nombre__icontains=search) |
                                                       Q(identificacion__icontains=search) |
                                                       Q(alias__icontains=search))
            else:
                proveedores = Proveedor.objects.all()

            paging = MiPaginador(proveedores, 25)
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
            data['proveedores'] = page.object_list
            return render_to_response("proveedores/proveedores.html", data)
