import json
import pdb

from django.shortcuts import render
from .forms import *
from .utils import *
from django.shortcuts import redirect
from django.http import JsonResponse


# Create your views here.
def first_step(request):
    if request.method == 'POST':
        for key in request.POST.keys():
            if key == 'csrfmiddlewaretoken':
                continue
            request.session[key] = request.POST[key]
        return redirect('/second-step')
    else:
        request.session.flush()

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
        if k == 'numVar' or k == 'numRest' or k == 'method' or k == 'objective' or k == "exibition_type" or k == 'integer_solution':
            continue

        if 'a' in str(k):
            restr.append(v)
        else:
            funcObj.append(int(v))

    restrictions = treat_restrictions(restr, int(request.session["numVar"]))

    requestJson = {
        "method": request.session["method"],
        "objective": request.session["objective"],
        "objective_function": funcObj,
        "restrictions": restrictions,
    }

    if "integer_solution" in request.session.keys():
        requestJson["integerSolution"] = request.session["integer_solution"] == 'on'

    #requestJson = json.dumps(requestJson)

    #return render(request, 'resultado.html')
    return JsonResponse(requestJson)


# https://getbootstrap.com/docs/4.3/components/forms/