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
            request.session[f'x{i:02d}'] = request.POST[f'x{i:02d}']

        for i in range(numRest):
            for j in range(numVar + 2):
                request.session[f'a{i:02d}{j:02d}'] = request.POST[f'a{i:02d}{j:02d}']

        return redirect(url)
    else:
        if "numVar" not in request.session.keys():
            return redirect('')

        numVar = int(request.session['numVar'])
        numRest = int(request.session['numRest'])
        form = SecondStepForm(numVar, numRest)

        return render(request, 'formulario2.html', {'form': form, 'numVar': range(numVar), 'numRest': range(numRest)
            , 'classCol': f'col-sm-{int(10 / (numVar + 1))}', 'sliceRest': f'{1 + numVar}:'
            , 'sliceObjet': f'1:{numVar + 1}'})


def third_step(request):
    if request.session['exibition_type'] == "GRAFICA":
        return redirect('/grafica')
    else:
        return redirect('/tabular')


def get_chart_data(request):
    json_request = make_json(request.session)
    json_response = {"result": {"iterations_path": ["P0", "P2", "P3"], "iterations_count": 3, "variables": ["x1", "x2"],
                                "points": [{"coords": [0.0, 0.0], "label": "P0", "value": 0.0},
                                           {"coords": [0.0, 3.0], "label": "P1", "value": 6.0},
                                           {"coords": [3.0, 0.0], "label": "P2", "value": 9.0},
                                           {"coords": [2.0, 2.0], "label": "P3", "value": 10.0}], "points_count": 4,
                                "optimum_point": "P3", "optimum_value": 10.0, "has_multiple_solution": False,
                                "multiple_solutions": []}, "status": 0, "ellapsed_time": 1.9984245300292969,
                     "error_msg": ""}
    return JsonResponse(json_response)


def tabular_view(request):
    json_request = make_json(request.session)
    json_response = {"result": {"optimum_point": [2.0, 2.0, 0.0, 0.0], "optimum_value": 10.0, "iterations": [
                    {"z": {"coeficients": [-3.0, -2.0, -0.0, -0.0], "value": 0},
                    "expressions": [{"coeficients": [2.0, 1.0, 1.0, 0.0], "value": 6, "base": "sx3"},
                     {"coeficients": [1.0, 2.0, 0.0, 1.0], "value": 6, "base": "sx4"}],
                    "base_variables": ["sx3", "sx4"], "target_point": [0.0, 0.0, 6.0, 6.0], "base_in": "x1", "base_out": "sx3",
                    "is_optimum": False}, {"z": {"coeficients": [0.0, -0.5, 1.5, 0.0], "value": 9.0},
                    "expressions": [{"coeficients": [1.0, 0.5, 0.5, 0.0], "value": 3.0, "base": "x1"},
                    {"coeficients": [0.0, 1.5, -0.5, 1.0], "value": 3.0, "base": "sx4"}],
                    "base_variables": ["x1", "sx4"], "target_point": [3.0, 0.0, 0.0, 3.0], "base_in": "x2",
                    "base_out": "sx4", "is_optimum": False},
                    {"z": {"coeficients": [0.0, 0.0, 1.3333333333333333, 0.3333333333333333], "value": 10.0}, "expressions": [
                    {"coeficients": [1.0, 0.0, 0.6666666666666666, -0.3333333333333333], "value": 2.0, "base": "x1"},
                    {"coeficients": [0.0, 1.0, -0.3333333333333333, 0.6666666666666666], "value": 2.0, "base": "x2"}],
                    "base_variables": ["x1", "x2"], "target_point": [2.0, 2.0, 0.0, 0.0], "base_in": "", "base_out": "",
                    "is_optimum": True}], "iterations_count": 3, "variables": ["x1", "x2", "sx3", "sx4"],
                    "input_variables": ["x1", "x2"], "slack_variables": ["sx3", "sx4"],
                    "artificial_variables": []}, "status": 0, "ellapsed_time": 1.9989013671875,
                    "error_msg": ""}

    headers = ["Base", "z"] + json_response["result"]["variables"] + ["b"]
    interactions = json_response["result"]["iterations"]
    optimum_point =  json_response["result"]["optimum_point"]
    optimum_value = json_response["result"]["optimum_value"]
    tables = []

    for iter in interactions:
        current_table = []
        lineZ = ["z", "1"] + iter["z"]["coeficients"]
        lineZ.append(iter["z"]["value"])
        current_table.append(lineZ)

        for exp in iter["expressions"]:
            current_line = [exp["base"], "0"] + exp["coeficients"]
            current_line.append(exp["value"])
            current_table.append(current_line)

        tables.append(current_table)

    return render(request, 'resultado_tabular.html',
                  context={"tables":tables, "headers": headers, "optimum_point":optimum_point,
                           "optimum_value": optimum_value})


def graphic_view(request):
    return render(request, 'resultado_grafico.html')

# https://getbootstrap.com/docs/4.3/components/forms/
