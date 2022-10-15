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
        numVar = request.POST['numVar']
        numRest = request.POST['numRest']
        return redirect(f'/second-step?numVar={numVar}?numRest={numRest}')
    else:
        form = FirstStepForm()
        return render(request, 'formulario.html', {'form': form})


def second_step(request):
    if request.method == 'POST':
        baseurl = str(request.build_absolute_uri())
        values = baseurl.split('?')
        numVar = int(values[1].split('=')[1])
        numRest = int(values[2].split('=')[1])
        url = f'/result?numVar={numVar}'
        for i in range(0, numRest):
            url += '?' + request.POST[f'restricao {i}']
        print(url)
        return redirect(url)
    else:
        baseurl = str(request.build_absolute_uri())
        values = baseurl.split('?')
        numVar = int(values[1].split('=')[1])
        numRest = int(values[2].split('=')[1])
        form = SecondStepForm(numRest)
        return render(request, 'formulario2.html', {'form': form})


def third_step(request):
    baseurl = unquote(str(request.build_absolute_uri()))
    values = baseurl.split('?')
    # chart = get_chart()

    numVar = values[1]
    restr = values[2:]
    # util_area = get_area(values, numVar)
    util_area = [
        [-1, 0, 0],  # x₁ ≥ 0
        [0, -1, 0],  # x₂ ≥ 0
        [-1, 1, -2],  # -x₁ + x₂ ≤ 2
        [1, 0, -4],  # x₁ ≤ 4
        [0, 1, -4],  # x₂ ≤ 4
    ]
    print(util_area)
    feasible_point = np.array([0.5, 0.5])
    # xmin = min(util_area[:][0])
    # ymin = min(util_area[:][1])
    xlim = (-1, 5)
    area_chart = render_inequalities(util_area, feasible_point, xlim, xlim)
    context = {
        'chart': area_chart
    }

    return render(request, 'resultado.html', context)
