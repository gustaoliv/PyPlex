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
        pieces = value.split('=')

        pieces = pieces[0].split('+') + list(pieces[1])
        coeficients = []
        for piece in pieces:
            if(not piece.strip()):
                continue

            coef = piece.strip().split('x')[0]
            if(coef == ''):
                coef = 1
            else:
                coef = int(coef)

            coeficients.append(coef)

        util_area.append(coeficients)

    return util_area


def render_inequalities(halfspaces, feasible_point, xlim, ylim):
    hs = HalfspaceIntersection(np.array(halfspaces), np.array(feasible_point))
    fig = pyplot.figure()
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    x = np.linspace(*xlim, 100)

    for h in halfspaces:
        if h[1]== 0:
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