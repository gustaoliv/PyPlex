from django.shortcuts import render
from django import forms
from .forms import *
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

# Create your views here.

def home(request):
    return render(request, 'index.html')


def first_step(request):
    if(request.method == 'POST'):
        numVar  = request.POST['numVar']
        numRest = request.POST['numRest']
        return redirect(f'/second-step?numVar={numVar}?numRest={numRest}')
    else:
        form = FirstStepForm()
        return render(request, 'formulario.html', {'form': form})


def second_step(request):
    if(request.method == 'POST'):
        baseurl = str(request.build_absolute_uri())
        values  = baseurl.split('?')
        numVar  = int(values[1].split('=')[1])
        numRest = int(values[2].split('=')[1])
        url = '/result'
        for i in range(0, numRest):
            url += '?' + request.POST[f'restricao {i}']
        print(url)
        return redirect(url)
    else:
        baseurl = str(request.build_absolute_uri())
        values  = baseurl.split('?')
        numVar  = int(values[1].split('=')[1])
        numRest = int(values[2].split('=')[1])
        form    = SecondStepForm(numRest)
        return render(request, 'formulario2.html', {'form': form})


def third_step(request):
    baseurl = str(request.build_absolute_uri())
    values  = baseurl.split('?')

    return render(request, 'resultado.html')