#! /usr/bin/env python
# -*- coding: utf-8 -*-

import string
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from store.forms import CambioClaveForm
from store.functions import addUserData
from store.models import ModuloGrupo
from store.values import NOMBRE_INSTITUCION


@login_required(redirect_field_name='ret', login_url='/login')
def index(request):
    data = {'title': 'Welcome - MiniMarket App'}
    addUserData(request, data)
    data['grupos'] = ModuloGrupo.objects.all()
    if 'info' in request.GET:
        data['info'] = request.GET['info']
    return render_to_response("panelbs.html", data)


def login_user(request):
    if request.method == 'POST':
        user = authenticate(username=string.lower(request.POST['username']), password=request.POST['password'])
        if user is not None:
            if not user.is_active:
                return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=3")
            else:
                login(request, user)
                return HttpResponseRedirect(request.POST['ret'])
        else:
            return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=1")
    else:
        ret = '/'
        if 'ret' in request.GET:
            ret = request.GET['ret']
        return render_to_response("login.html",
                                  {
                                      "title": "Login",
                                      "return_url": ret,
                                      "error": request.GET['error'] if 'error' in request.GET else "",
                                      "request": request,
                                      "nombreinstitucion": NOMBRE_INSTITUCION,
                                      "currenttime": datetime.now()
                                  })


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required(redirect_field_name='ret', login_url='/login')
def passwd(request):
    data = {'title': 'Change Password', 'form': CambioClaveForm()}
    addUserData(request, data)
    if request.method == 'POST':
        f = CambioClaveForm(request.POST)
        if f.is_valid():
            data = {}
            addUserData(request, data)
            user = data['usuario']
            if user.check_password(f.cleaned_data['anterior']):
                user.set_password(f.cleaned_data['nueva'])
                user.save()
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/pass?error=keys')
        return HttpResponseRedirect('/pass?error=form')
    else:

        if 'error' in request.GET:
            errorNo = request.GET['error']
            if errorNo == 'keys':
                data['formerror'] = 'Before password does not match'
            elif errorNo == 'form':
                data['formerror'] = 'There is an error in forms fields'
        return render_to_response("changepassbs.html", data)
