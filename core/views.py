import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from plotly.offline import plot
import simplex.main
from .forms import *
from .utils import *


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
            messages.error(request, 'Algo de inesperado aconteceu. Verifique as entradas.')
            return redirect('/')


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
        output_data = json.loads(json_response)

        if len(json_response["error_msg"]) > 0:
            raise Exception("Solution Error:" + output_data ["error_msg"])

        headers = ["Base", "z"] + output_data ["result"]["variables"] + ["b"]
        interactions = output_data ["result"]["iterations"]
        optimum_point = output_data ["result"]["optimum_point"]
        optimum_value = output_data["result"]["optimum_value"]
        tables = []

        for iter in interactions:
            index_base_in = headers.index(iter["base_in"]) if iter["base_in"] in headers else -1

            current_table = []
            line_z = ["z", "1"] + iter["z"]["coeficients"]
            line_z.append(iter["z"]["value"])
            treated_line_z = []
            for value in line_z:
                treated_line_z.append({"tag": "normal", "value": value})

            if index_base_in >= 0:
                treated_line_z[index_base_in]["tag"] = "bold"
            current_table.append(treated_line_z)

            for exp in iter["expressions"]:
                tag = "bold" if exp["base"] == iter["base_out"] else "normal"

                current_line = [exp["base"], "0"] + exp["coeficients"]
                current_line.append(exp["value"])
                treated_line = []
                for value in current_line:
                    treated_line.append({"tag": tag, "value": value})

                if index_base_in >= 0:
                    treated_line[index_base_in]["tag"] = "bold"
                current_table.append(treated_line)

            tables.append(current_table)

        context = {"tables": tables, "headers": headers, "optimum_point": optimum_point,"optimum_value": optimum_value}

        return render(request, 'resultado_tabular.html', context=context)
    except Exception as e:
        print(e)
        messages.error(request, 'Algo de inesperado aconteceu. Verifique as entradas.')
        return redirect('/')


def graphic_view(request):
    try:
        input_data = make_json(request.session)
        json_request = json.dumps(input_data)
        json_response = simplex.main.solve_simplex(json_request)
        output_data = json.loads(json_response)

        if len(output_data["error_msg"]) > 0:
            raise Exception("Solution Error:" + output_data["error_msg"])

        # Create rescrictions coordinates
        optimum_point = output_data["result"]["optimum_point"]
        optimum_value = output_data["result"]["optimum_value"]
        restrictions = []
        vertical_rescritions = [0, ]
        horizontal_restrictions = [0, ]
        max_x = 0
        max_y = 0

        for restrict in input_data["restrictions"][:-len(input_data["variable_names"])]:
            coord = []

            if restrict["coeficients"][0] == 0:
                horizontal_restrictions.append(restrict["value"] / restrict["coeficients"][1])
                continue
            elif restrict["coeficients"][1] == 0:
                vertical_rescritions.append(restrict["value"] / restrict["coeficients"][0])
                continue

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
        sorted_data = data.sort_values(by=['lables'])

        # Create graphic base
        layout = go.Layout(
            autosize=True,
            dragmode="pan",
            margin=dict({'b': 0, 'l': 0, 'r': 0, 't': 0}))
        fig = go.Figure(layout=layout)

        # plot restrictions
        for restrict in restrictions:
            fig.add_annotation(
                ax=restrict[0][0], axref='x',
                ay=restrict[0][1], ayref='y',
                x=restrict[1][0], xref='x',
                y=restrict[1][1], yref='y', arrowwidth=3, arrowcolor="red")

        for point in horizontal_restrictions:
            fig.add_hline(y=point, line_color="red", line_width=3)
        for point in vertical_rescritions:
            fig.add_vline(x=point, line_color="red", line_width=3)

        # plot points and available area
        fig.add_trace(go.Scatter(x=sorted_data["x"], y=sorted_data["y"], text=sorted_data["lables"],
                                 mode='lines+markers+text',
                                 marker_size=[20] * len(x), marker_color="green",
                                 fill='toself', fillcolor='#00CC96', textposition="top right"))

        # plot arrows
        indexed_data = data.set_index("lables")
        for i in range(len(output_data["result"]["iterations_path"]) - 1):
            fig.add_annotation(
                ax=indexed_data.filter(items=[output_data["result"]["iterations_path"][i]], axis=0)["x"][0], axref='x',
                ay=indexed_data.filter(items=[output_data["result"]["iterations_path"][i]], axis=0)["y"][0], ayref='y',
                x=indexed_data.filter(items=[output_data["result"]["iterations_path"][i + 1]], axis=0)["x"][0],
                xref='x',
                y=indexed_data.filter(items=[output_data["result"]["iterations_path"][i + 1]], axis=0)["y"][0],
                yref='y',
                arrowwidth=3, arrowhead=2)

        # Create countour plot lines
        quant_lines = 20
        first_mmc = output_data["result"]["optimum_value"]
        steps = first_mmc / quant_lines
        contours = []
        for value in np.arange(0, first_mmc + 1, steps):
            contour = []
            # x = 0
            try:
                contour.append([0, value / input_data["objective_function"][1]])
            except:
                contour.append([0, 0])
            # y = 0
            try:
                contour.append([value / input_data["objective_function"][0], 0])
            except:
                contour.append([0, 0])

            contours.append(contour)

        # plot contours
        for contour in contours:
            fig.add_annotation(
                ax=contour[0][0], axref='x',
                ay=contour[0][1], ayref='y',
                x=contour[1][0], xref='x',
                y=contour[1][1], yref='y', arrowwidth=1, arrowcolor="blue")

        config = {'responsive': True}

        graph = plot(fig, output_type="div", config=config)

        context = {"graph": graph, "optimum_point": optimum_point, "optimum_value": optimum_value}

        if bool(output_data["result"]["has_multiple_solution"]):
            context["multiple_solutions"] = output_data["result"]["multiple_solutions"]

        if "integer_solution" in output_data["result"].keys():
            context["integer_solution"] = output_data["result"]["integer_solution"]

        return render(request, 'resultado_grafico.html', context=context)

    except Exception as e:
        print(e)
        messages.error(request, 'Algo de inesperado aconteceu. Verifique as entradas.')
        return redirect('/')
