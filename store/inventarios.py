#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render_to_response

from store.functions import MiPaginador
from store.models import InventarioReal
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': 'Inventories'}
    addUserData(request, data)

    search = None
    if 's' in request.GET:
        search = request.GET['s']

    if search:
        inventarios = InventarioReal.objects.filter(Q(producto__codigo__icontains=search) |
                                                    Q(producto__descripcion__icontains=search),
                                                    producto__activo=True)
    else:
        inventarios = InventarioReal.objects.all()

    paging = MiPaginador(inventarios, 25)
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
    data['inventarios'] = page.object_list
    data['search'] = search if search else ""

    return render_to_response("inventarios/inventarios.html", data)
