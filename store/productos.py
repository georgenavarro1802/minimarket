#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from store.forms import ProductoForm, FotoProductoForm
from store.functions import MiPaginador, url_back, mensaje_excepcion, ok_json, bad_json, salva_auditoria
from store.models import Producto, TipoProducto
from store.values import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Products'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ProductoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        producto = Producto(codigo=f.cleaned_data['codigo'],
                                            codigobarra=f.cleaned_data['codigobarra'],
                                            descripcion=f.cleaned_data['descripcion'],
                                            unidadmedida=f.cleaned_data['unidadmedida'],
                                            tipoproducto=f.cleaned_data['tipoproducto'],
                                            alias=f.cleaned_data['alias'],
                                            pvp=f.cleaned_data['pvp'])
                        producto.save()
                        salva_auditoria(request, producto, ACCION_ADICIONAR)
                        return ok_json()
                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            producto = Producto.objects.get(pk=request.POST['id'])
            f = ProductoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        producto.codigo = f.cleaned_data['codigo']
                        producto.codigobarra = f.cleaned_data['codigobarra']
                        producto.descripcion = f.cleaned_data['descripcion']
                        producto.unidadmedida = f.cleaned_data['unidadmedida']
                        producto.tipoproducto = f.cleaned_data['tipoproducto']
                        producto.alias = f.cleaned_data['alias']
                        producto.pvp = f.cleaned_data['pvp']
                        producto.save()
                        salva_auditoria(request, producto, ACCION_MODIFICAR)
                        return ok_json()
                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=1)

        elif action == 'delete':
            producto = Producto.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, producto, ACCION_ELIMINAR)
                    producto.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        elif action == 'cargarfoto':
            producto = Producto.objects.get(pk=request.POST['id'])
            form = FotoProductoForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        foto = request.FILES['foto']
                        if foto:
                            producto.foto = foto
                            producto.save()
                        return ok_json()
                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=1)

        elif action == 'actualizacodigoprod':
            try:
                tipoprod = TipoProducto.objects.get(pk=request.POST['tipoid'])
                if tipoprod.producto_set.exists():
                    nuevocodigo = tipoprod.producto_set.latest('id').codigo + 1
                else:
                    nuevocodigo = tipoprod.inicial + 1
                return ok_json(data={"nuevocodigo": str(nuevocodigo)})
            except Exception:
                return bad_json()

        elif action == 'favorito':
            try:
                producto = Producto.objects.get(pk=request.POST['idprod'])
                if producto.esfavorito:
                    producto.esfavorito = False
                else:
                    producto.esfavorito = True
                producto.save()
                return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")

            except Exception as ex:
                return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")

        elif action == 'existencia':
            try:
                producto = Producto.objects.get(pk=request.POST['idprod'])
                if producto.tieneinv:
                    producto.tieneinv = False
                else:
                    producto.tieneinv = True
                producto.save()
                return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")

            except Exception as ex:
                return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = 'Add Product'
                    form = ProductoForm()
                    form.for_addproducto()
                    data['form'] = form
                    return render_to_response('productos/add.html', data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = 'Edit Product'
                    data['producto'] = producto = Producto.objects.get(pk=request.GET['id'])
                    initial = model_to_dict(producto)
                    form = ProductoForm(initial=initial)
                    form.for_editproducto()
                    data['form'] = form
                    return render_to_response('productos/edit.html', data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = 'Delete Product'
                    data['producto'] = producto = Producto.objects.get(pk=request.GET['id'])
                    return render_to_response('productos/delete.html', data)
                except Exception as ex:
                    pass

            elif action == 'cargarfoto':
                try:
                    data['title'] = 'Upload Photo'
                    data['producto'] = Producto.objects.get(pk=request.GET['id'])
                    data['form'] = FotoProductoForm()
                    return render_to_response('productos/cargarfoto.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None
            tipo = None

            if 't' in request.GET:
                tipo = request.GET['t']

            if 's' in request.GET:
                search = request.GET['s']

            if search:
                productos = Producto.objects.filter(Q(codigo__icontains=search) |
                                                    Q(codigobarra__icontains=search) |
                                                    Q(descripcion__icontains=search))
            elif tipo:
                productos = Producto.objects.filter(tipoproducto__id=tipo)
            else:
                productos = Producto.objects.filter(activo=True)

            paging = MiPaginador(productos, 50)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(p)

            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['productos'] = page.object_list
            data['tipos_productos'] = TipoProducto.objects.all()
            data['tipoid'] = int(tipo) if tipo else ""
            return render_to_response("productos/productos.html", data)
