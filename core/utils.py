import uuid, base64
from .models import *
from io import BytesIO
from matplotlib import pyplot
import numpy as np
import pdb
from scipy.spatial import HalfspaceIntersection, ConvexHull
from matplotlib.patches import Polygon


def get_graph():
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_chart():
    pyplot.switch_backend('AGG')
    fig = pyplot.figure(figsize=(10, 4))
   
    xpoints = np.array([1, 2, 6, 8])
    ypoints = np.array([3, 8, 1, 10])
    pyplot.plot(xpoints, ypoints)

    pyplot.tight_layout()
    chart = get_graph()

    return chart


def get_area(restr, numVar):
    util_area = []
    for value in restr:
        if '<=' in value:
            pieces = value.split('<=')
            res = '-' + pieces[1]
            pieces = pieces[0].split('+')
            pieces.append(res)
            coeficients = []
            for piece in pieces:
                if not piece.strip():
                    continue

                coef = piece.strip().split('x')[0]
                if coef == '':
                    coef = 1
                elif coef == '-':
                    coef = -1
                else:
                    coef = int(coef)
                coeficients.append(coef)

            util_area.append(coeficients)
        else:
            pieces = value.split('>=')
            res = pieces[1]
            pieces = pieces[0].split('+')
            pieces.append(res)
            coeficients = []
            for piece in pieces:
                if not piece.strip():
                    continue
                if 'x' in coef:
                    coef = '-' + piece.strip().split('x')[0]
                else:
                    coef = piece.strip().split('x')[0]
                if coef == '':
                    coef = 1
                elif coef == '-':
                    coef = -1
                else:
                    coef = int(coef)
                coeficients.append(coef)

            util_area.append(coeficients)


    for i in range(numVar):
        line = list(np.zeros(numVar + 1))
        line[i] = -1
        util_area.append(line)

    return util_area


def render_inequalities(halfspaces, feasible_point, xlim, ylim):
    hs = HalfspaceIntersection(np.array(halfspaces), np.array(feasible_point))
    fig = pyplot.figure()
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    x = np.linspace(*xlim, 100)

    for h in halfspaces:
        if h[1] == 0:
            ax.axvline(-h[2]/h[0], color="#2c3e50")
        else:
            ax.plot(x, (-h[2]-h[0]*x)/h[1], color="#2c3e50")
    x, y = zip(*hs.intersections)
    points = list(zip(x, y))
    convex_hull = ConvexHull(points)
    polygon = Polygon([points[v] for v in convex_hull.vertices], color="#77dd77")
    ax.add_patch(polygon)
    ax.plot(x, y, 'o', color="#e67e22")

    chart = get_graph()

    return chart


def treat_restrictions(restrictions, num_variables):
    restrictions_list = []

    current_restriction = []
    for i in range(0, len(restrictions)):
        current_restriction.append(restrictions[i])
        if len(current_restriction) == num_variables + 2:
            restrictions_list.append({
                "coeficients": [int(val) for val in current_restriction[:-2]],
                "type": current_restriction[-2],
                "value": int(current_restriction[-1])
            })

            current_restriction = []

    for i in range(int(num_variables)):
        current_restriction = list(range(int(num_variables)))
        current_restriction = [x * 0 for x in current_restriction]
        current_restriction[i] = 1
        restrictions_list.append({
            "coeficients": current_restriction,
            "type": ">=",
            "value": 0
        })

    return restrictions_list


def make_json(session_dict):
    restr = []
    funcObj = []
    for k, v in session_dict.items():
        if k == 'numVar' or k == 'numRest' or k == 'method' or k == 'objective' or k == "exibition_type" or k == 'integer_solution':
            continue

        if 'a' in str(k):
            restr.append(v)
        else:
            funcObj.append(int(v))

    restrictions = treat_restrictions(restr, int(session_dict["numVar"]))

    requestJson = {
        "method": session_dict["method"],
        "objective": session_dict["objective"],
        "objective_function": funcObj,
        "restrictions": restrictions,
    }

    if "integer_solution" in session_dict.keys():
        requestJson["integerSolution"] = session_dict["integer_solution"] == 'on'

    var_names = []
    for i in range(1, int(session_dict["numVar"]) + 1):
        var_names.append(f"x{i}")

    requestJson["variable_names"] = var_names

    return requestJson


def mmc(nums):
    max_ = max(nums)
    i = 1
    while True:
        mult = max_ * i
        if all(mult%nr == 0 for nr in nums):
            return mult
        i += 1