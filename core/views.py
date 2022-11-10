import json
from ctypes import util
from django.shortcuts import render
from django import forms
from .forms import *
from .utils import *
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from urllib.parse import unquote


# Create your views here.


def home(request):
    return render(request, 'index.html')


def first_step(request):
    if request.method == 'POST':
        request.session['algMethod'] = request.POST['method']
        request.session['numVar'] = request.POST['numVar']
        request.session['numRest'] = request.POST['numRest']
        return redirect('/second-step')
    else:
        for key in list(request.session.keys()):
            del request.session[key]
        form = FirstStepForm()
        return render(request, 'formulario.html', {'form': form})


def second_step(request):
    if request.method == 'POST':
        numVar = int(request.session['numVar'])
        numRest = int(request.session['numRest'])
        url = '/result'

        request.session['objective'] = request.POST['objective']

        for i in range(numVar):
            request.session[f'x{i}'] = request.POST[f'x{i}']

        for i in range(numRest):
            for j in range(numVar + 2):
                request.session[f'a{i}{j}'] = request.POST[f'a{i}{j}']

        return redirect(url)
    else:
        numVar = int(request.session['numVar'])
        numRest = int(request.session['numRest'])
        form = SecondStepForm(numVar, numRest)

        return render(request, 'formulario2.html', {'form': form, 'numVar': range(numVar), 'numRest': range(numRest)
                      , 'classCol': f'col-sm-{int(10 / (numVar + 1))}', 'sliceRest': f'{1+numVar}:'
                      , 'sliceObjet': f'1:{numVar + 1}'})


def third_step(request):

    restr = []
    funcObj = []
    for k, v in request.session.items():
        if k == 'numVar' or k == 'numRest' or k == 'algMethod' or k == 'objective':
            continue

        if 'a' in str(k):
            restr.append(v)
        else:
            funcObj.append(int(v))

    restrictions = treat_restrictions(restr, int(request.session["numVar"]))

    requestJson = {
        "method": request.session["algMethod"],
        "objective": request.session["objective"],
        "objective_function": funcObj,
        "restrictions": restrictions,
    }

    requestJson = json.dumps(requestJson)

    pdb.set_trace()

    return render(request, 'resultado.html')
