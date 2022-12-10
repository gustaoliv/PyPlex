import json
import sys
import numpy as np
from simplex import graphic_methods as gm
from simplex import convertions

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    
    #Get the extended problem
    #try:
    #    configs = convertions.extended_problem(configs)
    #except Exception as e:
    #    output["status"] = -1
    #    output["error_msg"] = "Unable to define the extended problem. Error: " + e.__str__()
    #    return
    
    (viable_region, start_point) = gm.viability_region(configs)
    if len(viable_region) == 0:
        output["status"] = -1
        output["error_msg"] = "There is no viable points"
        return -1
    
    visited_points = []

    #Process the objective function to define the variable priorities
    obj_f = configs["objective_function"]
    for i in range(0, len(obj_f)):
        if obj_f[i] == "M":
            obj_f[i] = 1000000.0

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

            if configs["objective"] == "MAXIMIZE":
                if p["value"] >= next["value"]:
                    next = p
            else:
                if p["value"] <= next["value"]:
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
    result["variables"] = configs["variable_names"]
    number_of_vars = len(configs["variable_names"])

    for p in viable_region:
        if "value" not in p:
            p["value"] = 0
        
        result["points"].append({
            "coords": convertions.round_list(p["coords"][0:number_of_vars]),
            "label": p["label"],
            "value": round(p["value"], convertions.PRECISION)
        })

    result["points_count"] = len(result["points"])
    result["optimum_point"] = optimum_point["label"]
    result["optimum_value"] = round(optimum_point["value"], convertions.PRECISION)
    output["result"] = result
