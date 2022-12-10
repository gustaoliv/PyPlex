import numpy as np
import itertools
from simplex import convertions

#This function must get all the restriction intercections and compose a list with the label and coordenades

def viability_region(configs):
    restrictions = configs["restrictions"]
    num_of_restrictions = len(restrictions)
    if num_of_restrictions == 0:
        return None
    
    num_of_coeficients = len(restrictions[0]["coeficients"])

    points = []
    points_count = 0

    #If the problem have an artificial variable, converts the value 'M' to infinity
    new_restrictions = []
    for r in restrictions:
        if not convertions.is_inferior_limit_restriction(r) and is_dependent_restriction(r):
            continue
        new_r = r.copy()
        new_r["coeficients"] = list(map(lambda a : float('inf') if a == 'M' else a, r["coeficients"]))
        new_restrictions.append(new_r)

    restrictions = new_restrictions

    #The first thing to do is to combine the restrictions in a way that it can be solved later
    combinations = itertools.combinations(restrictions, num_of_coeficients)
    
    #Then we iterate over each combination, trying to solve it and get the intersection point
    for item in combinations:
        #The rigth way is to prealocate the objects below, but I couldn't do it
        coeficients = []
        values = []
        #Join all coeficients and values
        for i in range(0, num_of_coeficients):
            coeficients.append(np.array(item[i]["coeficients"]))
            values.append(item[i]["value"])
        #Solve it
        try:
            x = convertions.round_list(np.linalg.solve(coeficients, values))
            points.append({"label": "", "coords": x, "restrictions": item})
            points_count += 1
        except Exception as e:
            #The intersection is a line or it doesn't exists
            continue
    
    #Verify if the points meets all the restrictions
    viable_points = []
    for i in range(0, points_count):
        p = points[i]
        viable = True
        for r in restrictions:
            value = round(np.dot(np.array(r["coeficients"]), p["coords"]), 1)
            match (r["type"]):
                case ">=":
                    viable = (value >= r["value"] or np.isclose(value, r["value"]))
                case "<=":
                    viable = (value <= r["value"] or np.isclose(value, r["value"]))
                case "=":
                    viable = np.isclose(value, r["value"])
            if (not viable):
                break
        else:
            viable_points.append(p)
    """
        So, here the points object contains all the viable points of the problem.
        If there is 2 points, the region is a line.
        If we have just 2 variables and more then 2 points, we can have a surface.
        And if the problem have more then 2 variable, the result may be the edges of a multidimencional object.
    """
    start_point = get_start_point(viable_points, configs)
    insert_points_label(restrictions, viable_points, start_point)
    link_points(viable_points)
    return (viable_points, start_point)

def get_start_point(points, configs):
    if len(points) == 0:
        return -1
    
    if configs.keys().__contains__("extended_problem"):
        vars = len(configs["variable_names"])
        for p in points:
            for n in range(0,vars):
                if p["coords"][n] != 0:
                    break
            else:
                return p
    else:
        s = points[0]
        l = len(s["coords"])
        for i in range(1,len(points)):
            p = points[i]
            for j in range(0,l):
                if(p["coords"][j] > s["coords"][j]):
                    break
            else:
                s = p
        return s
    
    print("Couldn't find initial point.")
    return -1

def insert_points_label(restrictions, points, start):
    if len(points[0]["coords"]) > 2:
        return
    
    relationships = []
    for r in restrictions:
        arr = []
        for p in points:
            if p["restrictions"].__contains__(r):
                arr.append(p)
        relationships.append(arr)

    DEFAULT_DIRECTION = 0
    current_restriction = start["restrictions"][DEFAULT_DIRECTION]
    current_point = start
    counter = 0
    while True:
        current_point["label"] = "P"+str(counter)
        counter+=1

        index = restrictions.index(current_restriction)
        relationships[index].remove(current_point)
        current_point = relationships[index][0]
        i = (current_point["restrictions"].index(current_restriction) + 1) % 2
        current_restriction = current_point["restrictions"][i]

        if current_point == start:
            break

def link_points(points):
    for p1 in points:
        p1["siblings"] = []
        for p2 in points:
            if p1 == p2:
                continue
            for r in p1["restrictions"]:
                if p2["restrictions"].__contains__(r):
                    p1["siblings"].append(p2)
                    break

def get_priority_list(list):
    #Basically, is just ordanate the list and store the index
    priorities = []

    ref = list.copy()
    l = len(ref)
    for i in range(0, l):
        index = -1
        max = -float("inf")
        for j in range(0, l):
            if priorities.__contains__(j):
                continue
            if ref[j] > max:
                index = j
                max = ref[index]
        priorities.append(index)
    
    return priorities

def have_priority(p1, p2, priority_list):
    for i in priority_list:
        if(p1["coords"][i] > p2["coords"][i]):
            return True
    return False

def calc_point_value(point, obj_function):
    return np.dot(np.array(point["coords"]), np.array(obj_function))

def dot(arr1, arr2):
    value = 0
    for n in range(0,len(arr1)):
        value += arr1[n] * arr2[n]
    return value

def is_dependent_restriction(r):
    if r["value"] != 0:
        return False

    for n in r["coeficients"]:
        if n < 0:
            return False

    return True