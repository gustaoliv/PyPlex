import json
import sys
import numpy as np
import graphic_methods as gm

PRECISION = 3

def round_list(arr = []):
    out = []
    for n in arr:
        out.append(round(n, PRECISION))
    return out

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    (viable_region, start_point) = gm.viability_region(configs)
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

            if p["value"] >= next["value"]:
                next = p
        if next == target_point:
            break

        target_point = next
    
    optimum_point = target_point

    #Check for multiple solutions
    multiple_solutions = []
    for p in visited_points:
        if p != optimum_point and p["value"] == optimum_point["value"]:
            multiple_solutions.append(p["label"])

    #Generate output data
    result = {
        "iterations_path": [],
        "iterations_count": 0,
        "variables": [],
        "points": [],
        "points_count": 0,
        "optimum_point": "",
        "optimum_value": 0,
        "has_multiple_solution": len(multiple_solutions) > 0,
        "multiple_solutions": multiple_solutions
    }
    visited_points.reverse()
    for p in visited_points:
        result["iterations_path"].append(p["label"])
    
    result["iterations_count"] = len(result["iterations_path"])
    if configs.keys().__contains__("extended_problem"):
        result["variables"] = configs["variable_names_extended"]
    else:
        result["variables"] = configs["variable_names"]
    
    for p in viable_region:
        if not "value" in p:
            p["value"] = "None"
        
        result["points"].append(
        {
            "coords": round_list(p["coords"]),
            "label": p["label"],
            "value": round(p["value"], PRECISION)
        })

    result["points_count"] = len(result["points"])
    result["optimum_point"] = optimum_point["label"]
    result["optimum_value"] = round(optimum_point["value"], PRECISION)
    output["result"] = result
