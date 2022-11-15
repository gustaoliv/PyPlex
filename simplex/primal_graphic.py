import json
import sys
import numpy as np
import graphic_methods as gm

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    (viable_region, start_point) = gm.viability_region(configs["restrictions"])
    if len(viable_region) == 0:
        output["status"] = -1
        output["error_msg"] = "There is no viable points"
        return -1
    
    visited_points = []

    #Process the objective function to define the variable priorities
    obj_f = configs["objective_function"]
    priorities = gm.get_priority_list(obj_f)

    #Run the algorithm until the solution is finded
    target_point = start_point
    start_point["value"] = gm.calc_point_value(start_point, obj_f)

    while True:
        visited_points.insert(0, target_point)

        next = target_point
        #Verify if have any better point around
        for p in target_point["siblings"]:
            if visited_points.__contains__(p):
                continue
            if "value" not in p:
                p["value"] = gm.calc_point_value(p, obj_f)

            if p["value"] > next["value"]:
                next = p
        if next == target_point:
            break

        target_point = next
    
    optimum_point = target_point

    #Generate output data
    result = {
        "iterations_path": [],
        "iterations_count": 0,
        "variables": [],
        "points": [],
        "points_count": 0,
        "optimum_point": "",
        "optimum_value": 0,
        "has_multiple_solution": False,
        "multiple_solution": {}
    }
    visited_points.reverse()
    for p in visited_points:
        result["iterations_path"].append(p["label"])
    
    result["iterations_count"] = len(result["iterations_path"])
    result["variables"] = configs["variable_names"]
    
    for p in viable_region:
        if not "value" in p:
            p["value"] = "None"
        
        result["points"].append({"coords": np.ndarray.tolist(p["coords"]), "label": p["label"], "value": p["value"]})

    result["points_count"] = len(result["points"])
    result["optimum_point"] = optimum_point["label"]
    result["optimum_value"] = optimum_point["value"]
    output["result"] = result
