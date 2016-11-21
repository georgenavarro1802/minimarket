#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from store.functions import bad_json
from store.models import *
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': 'Reports'}
    addUserData(request, data)
    if 'action' in request.GET:
        action = request.GET['action']
        if action == 'data':
            try:
                m = request.GET['model']
                if 'q' in request.GET:
                    q = request.GET['q'].upper()
                    if ':' in m:
                        sp = m.split(':')
                        model = eval(sp[0])
                        query = model.flexbox_query(q)
                        for n in range(1,len(sp)):
                            query = eval('query.filter(%s)'%(sp[n]))
                    else:
                        model = eval(request.GET['model'])
                        query = model.flexbox_query(q)
                else:
                    model = eval(request.GET['model'])
                    query = model.flexbox_query('')

                data = {"results": [{"id": x.id, "name": x.flexbox_repr(), "alias": x.flexbox_alias()} for x in query]}
                return HttpResponse(json.dumps(data), content_type='application/json')

            except Exception as ex:
                return bad_json(error=1)

        return HttpResponseRedirect('/reportes')
    else:
        return render_to_response("reportes/reportesbs.html", data)