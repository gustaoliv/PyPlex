import json
import pdb
from django.shortcuts import render
import simplex.main
from .forms import *
from .utils import *
from django.shortcuts import redirect
from django.http import JsonResponse
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from simplex import *

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
       try:
            numVar = int(request.session['numVar'])
            numRest = int(request.session['numRest'])
            form = SecondStepForm(numVar, numRest)

            return render(request, 'formulario2.html', {'form': form, 'numVar': range(numVar), 'numRest': range(numRest)
                , 'classCol': f'col-sm-{int(10 / (numVar + 1))}', 'sliceRest': f'{1 + numVar}:'
                , 'sliceObjet': f'1:{numVar + 1}'})
       except:
           return  redirect('/')


def third_step(request):
    if request.session['exibition_type'] == "GRAPHIC":
        return redirect('/grafica')
    else:
        return redirect('/tabular')


def tabular_view(request):
    try:
        json_request = make_json(request.session)
        json_request = json.dumps(json_request)
        json_response = simplex.main.solve_simplex(json_request)
        json_response = json.loads(json_response)

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
    except Exception as e:
        print(e)
        pdb.set_trace()
        return redirect('/')


def graphic_view(request):
    try:
        input_data = make_json(request.session)
        json_request = json.dumps(input_data)
        json_response = simplex.main.solve_simplex(json_request)
        output_data = json.loads(json_response)

        #Create rescrictions coordinates
        optimum_point = output_data["result"]["optimum_point"]
        optimum_value = output_data["result"]["optimum_value"]
        restrictions = []
        max_x = 0
        max_y = 0

        for restrict in input_data["restrictions"][:-len(input_data["variable_names"])]:
            coord = []
            # x = 0
            try:
                coord.append([0, restrict["value"] / restrict["coeficients"][1]])
            except:
                coord.append([0, 0])
            # y = 0
            try:
                coord.append([restrict["value"] / restrict["coeficients"][0], 0])
            except:
                coord.append([0, 0])

            if coord[0][0] > max_x or coord[1][0] > max_x:
                max_x = max([coord[0][0], coord[1][0]])
            if coord[0][1] > max_y or coord[1][1] > max_y:
                max_y = max([coord[0][1], coord[1][1]])

            restrictions.append(coord)


        # Construct DataFrame
        x = []
        y = []
        lables = []
        values = []
        for coord in output_data["result"]["points"]:
            x.append(coord["coords"][0])
            y.append(coord["coords"][1])
            lables.append(coord["label"])
            values.append(coord["value"])

        data = pd.DataFrame({"x": x, "y": y, "lables": lables, "values": values})
        sorted_data = data.sort_values(by=['x'])

        # Create graphic base
        layout = go.Layout(
            autosize=True,
            dragmode="pan",
            margin=dict({'b': 0, 'l':0, 'r':0, 't':0}))
        fig = go.Figure(layout=layout)

        # plot restrictions
        restrictions.append([[0, 0], [max_x, 0]])
        restrictions.append([[0, 0], [0, max_y]])
        for restrict in restrictions:
            fig.add_annotation(
                ax=restrict[0][0], axref='x',
                ay=restrict[0][1], ayref='y',
                x=restrict[1][0],  xref='x',
                y=restrict[1][1], yref='y', arrowwidth=3, arrowcolor="red")


        # plot points and available area
        fig.add_trace(go.Scatter(x=sorted_data["x"], y=sorted_data["y"], text=sorted_data["lables"],
                                 mode='lines+markers+text',
                                 marker_size=[20]*len(x), marker_color = "green",
                                 textposition="top right"))


        # plot arrows
        indexed_data = data.set_index("lables")
        for i in range(len(output_data["result"]["iterations_path"]) - 1):
            fig.add_annotation(ax=indexed_data.filter(items=[output_data["result"]["iterations_path"][i]], axis=0)["x"][0], axref='x',
                               ay=indexed_data.filter(items=[output_data["result"]["iterations_path"][i]], axis=0)["y"][0], ayref='y',
                               x=indexed_data.filter(items= [output_data["result"]["iterations_path"][i+1]], axis=0)["x"][0], xref='x',
                               y=indexed_data.filter(items= [output_data["result"]["iterations_path"][i+1]], axis=0)["y"][0], yref='y',
                               arrowwidth=3, arrowhead=2)

        #Create countour plot lines
        quant_lines = 20
        first_mmc = output_data["result"]["optimum_value"]
        steps = first_mmc / quant_lines
        countours = []
        for value in np.arange(0, first_mmc + 1, steps):
            countour = []
            # x = 0
            try:
                countour.append([0, value/input_data["objective_function"][1]])
            except:
                countour.append([0, 0])
            #y = 0
            try:
                countour.append([value / input_data["objective_function"][0], 0])
            except:
                countour.append([0, 0])

            countours.append(countour)

        # plot contourns
        for countour in countours:
            fig.add_annotation(
                ax=countour[0][0], axref='x',
                ay=countour[0][1], ayref='y',
                x=countour[1][0],  xref='x',
                y=countour[1][1], yref='y', arrowwidth=1, arrowcolor="blue")

        config = {'responsive': True}

        graph = plot(fig, output_type="div", config=config)

        return render(request, 'resultado_grafico.html', context={"graph": graph, "optimum_point":optimum_point,
                               "optimum_value": optimum_value} )
    except Exception as e:
        print(e)
        pdb.set_trace()
        return redirect('/')
