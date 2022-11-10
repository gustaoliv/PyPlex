import numpy as np
import itertools

#This function must get all the restriction intercections and compose a list with the label and coordenades
def viability_region(restrictions):
    num_of_restrictions = len(restrictions)
    if num_of_restrictions == 0:
        return None
    
    num_of_coeficients = len(restrictions[0]["coeficients"])

    points = []
    points_count = 0

    #If the the problem have an artificial variable, converts the value 'M' to infinity
    for r in restrictions:
        r["coeficients"] = list(map(lambda a : float('inf') if a == 'M' else a, r["coeficients"]))
    
    #The first thing to do is to combine the restrictions in a way that is could be solved later
    combinations = itertools.combinations(restrictions, num_of_coeficients)
    
    #Then we iterate over each combination, trying to solve it and get the intersection point
    for item in combinations:
        #The rigth way is to prealocate the objects below, but I couldn't do it
        coeficients = []
        values = []
        #Join all coeficients and values
        for i in range(0, num_of_coeficients):
            coeficients.append(item[i]["coeficients"])
            values.append(item[i]["value"])

        #Solve it
        try:
            x = np.linalg.solve(coeficients, values)
            points.append({"label": "", "coords": x, "restrictions": item})
            points_count += 1
        except Exception as e:
            #The intersection is a line or it doesn't exists
            continue
    
    #Verify if the points meets all the restrictions
    print(restrictions)
    viable_points = []
    for i in range(0, points_count):
        p = points[i]
        viable = True
        for r in restrictions:
            value = np.dot(np.array(r["coeficients"]), p["coords"])
            match(r["type"]):
                case ">=":
                    viable = value >= r["value"]
                case "<=":
                    viable = value <= r["value"]
                case "=":
                    viable = value == r["value"]
            if(not viable):
                break
        else:
            viable_points.append(p)
    """
        So, here the points object contains all the viable points of the problem.
        If there is 2 points, the region is a line.
        If we have just 2 variables and more then 2 points, we can have a surface.
        And if the problem have more then 2 variable, the result may be the edges of a multidimencional object.
    """
    insert_points_label(viable_points)
    return viable_points

def start_point(points):
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

def insert_points_label(points):
    points_with_label = []
    s = start_point(points)
    s["label"] = "P0"
    points.remove(s)
    points_with_label.append(s)

    counter = 1
    current_point = s
    while len(points) > 0:
        for r in current_point["restrictions"]:
            for p in points:
                if p["restrictions"].__contains__(r):
                    p["label"] = "P"+str(counter)
                    current_point = p
                    points.remove(p)
                    points_with_label.append(p)
                    counter+=1
                    break
    
    points.extend(points_with_label)