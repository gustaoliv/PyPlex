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
        numVar = int(request.session['numVar'])
        numRest = int(request.session['numRest'])
        form = SecondStepForm(numVar, numRest)

        return render(request, 'formulario2.html', {'form': form, 'numVar': range(numVar), 'numRest': range(numRest)
                      , 'classCol': f'col-sm-{int(10 / (numVar + 1))}', 'sliceRest': f'{1+numVar}:'
                      , 'sliceObjet': f'1:{numVar + 1}'})


def third_step(request):
    if request.session['exibition_type'] == "GRAFICA":
        return redirect('/grafica')
    else:
        return redirect('/tabular')


def get_chart_data(request):
    json_request = make_json(request.session)
    json_response = {"result": {"iterations_path": ["A", "B", "C"],"iterations_count": 3,"variables": ["x1","x2"],"points": [{"label": "A","coords": [0,0]},{"label": "B","coords": [0,0]},{"label": "C","coords": [0,0]},{"label": "D","coords": [0,0]}],"points_count": 4,"optimum_point": "C","optimum_value": 10},"has_multiple_solution": False,"multiple_solution": {},"status": 0,"ellapsed_time": 0,"error_msg": ""}
    return JsonResponse(json_response)


def tabular_view(request):
    json_request = make_json(request.session)
    json_response = {"result": {"optimum_point": [2,2],"optimum_value": 10,"iterations": [{"expressions": [{"coeficients": [ -3, -2, 0, 0],"value": 0},{"coeficients": [2, 1, 1, 0],"value": 6},{"coeficients": [1, 2, 0, 1],"value": 6}],"base_variables": ["sx3","sx4"],"target_point": [0,0],"point_label": "A","base_in": "x1","base_out": "sx3","is_optimum": False},{"expressions": [{"coeficients": [0, -0.5, 1.5, 0],"value": 9},{"coeficients": [1, 0.5, 0.5, 0],"value": 3},{"coeficients": [0, 1.50, -0.5, 1],"value": 3}],"base_variables": ["x1","sx4"],"target_point": [3,0],"point_label": "B","base_in": "x2","base_out": "sx4","is_optimum": False},{"expressions": [{"coeficients": [0, 0, 1.33, 0.33],"value": 10},{"coeficients": [1, 0, 0.67, -0.33],"value": 2},{"coeficients": [0, 1, -0.33, 0.67],"value": 2}],"base_variables": ["x1","x2"],"target_point": [2,2],"point_label": "C","is_optimum": True}],"iterations_count": 3,"input_variables": ["x1","x2"],"slack_variables": ["sx3","sx4"],"virtual_variables": []},"multiple_solutions": [{"objective_function": [2, 5, 1],"optimum_point": [],"optimum_value": 0,"restrictions": [{"coeficients": [1,2],"type": "<=","value": 14},{"coeficients": [1,1],"type": "<=","value": 9},{"coeficients": [7,4],"type": "<=","value": 56}],"iterations": [{"expressions": [{"coeficients": [1,2],"type": "<=","value": 14},{"coeficients": [1,1],"type": "<=","value": 9},{"coeficients": [7,4],"type": "<=","value": 56}],"target_point": [0,0],"point_label": "A"}],"iterations_count": 0}],"status": 0,"ellapsed_time": 0,"error_msg": ""}
    iterations = json_response['result']["iterations"]

    table_result = []
    for iterat in iterations:
        expressions = iterat["expressions"]

        iterat_lines = []
        for value in expressions:
            iterat_lines.append(value['coeficients'])
            iterat_lines[-1].append(value['value'])

        white_line = []
        for i in range(len(iterat_lines[0])):
            white_line.append("")
        iterat_lines.append(white_line)

        table_result.append(iterat_lines)

    return render(request, 'resultado_tabular.html', context={'table_values': table_result, 'headers':['x1', 'x2', 'sx3', 'sx4', 'b']})


def graphic_view(request):
    return render(request, 'resultado_grafico.html')

# https://getbootstrap.com/docs/4.3/components/forms/