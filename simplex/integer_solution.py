import numpy as np
import math
from simplex.graphic_methods import dot
 
#Branch-and-Bound (B&B) method
def get_first_real_index(arr):
    for i in range(0, len(arr)):
        if arr[i] % 1 != 0:
            return i
    return -1

best_integer_point = None
def run(configs, output):
    def create_node(coords = [], value = None, viable = False, possible = False):
        return {
            "coords": coords,
            "value": value,
            "viable": viable,
            "possible": possible,
            "left": None,
            "right": None
        }
    
    def is_integer_solution(point):
        for i in range(0, len(point["coords"])):
            if round(point["coords"][i],3) % 1 != 0:
                return False
        return True
    
    def evaluate(point, best_integer_point):
        for r in configs["restrictions"]:
            value = dot(r["coeficients"], point["coords"])
            match(r["type"]):
                case ">=":
                    point["possible"] = value >= r["value"]
                case "<=":
                    point["possible"] = value <= r["value"]
                case "=":
                    point["possible"] = value == r["value"]
            if(not point["possible"]):
                return best_integer_point
        
        if is_integer_solution(point):
            point["viable"] = True
            if best_integer_point != None:
                if configs["problem_type"] == "MAXIMIZE" and point["value"] > best_integer_point["value"]:
                    best_integer_point = point
                elif configs["problem_type"] == "MINIMIZE" and point["value"] < best_integer_point["value"]:
                    best_integer_point = point
            else:
                best_integer_point = point
            return best_integer_point
            
        i = get_first_real_index(point["coords"])
        n = point["coords"][i]
        point["left"] = create_node(point["coords"].copy())
        point["left"]["coords"][i] = math.floor(n)
        point["left"]["value"] = dot(point["left"]["coords"], configs["objective_function"])
        best_integer_point = evaluate(point["left"], best_integer_point)

        point["right"] = create_node(point["coords"].copy())
        point["right"]["coords"][i] = math.ceil(n)
        point["right"]["value"] = dot(point["right"]["coords"], configs["objective_function"])
        best_integer_point = evaluate(point["right"], best_integer_point)
        return best_integer_point

    if not output["result"].keys().__contains__("input_variables"):
        output["result"]["input_variables"] = output["result"]["variables"]

    best_integer_point = None
    number_of_variables = len(output["result"]["input_variables"])

    optimum_label = output["result"]["optimum_point"]
    optimum_point = {}

    root = create_node(
        optimum_point["coords"][0:number_of_variables],
        float(output["result"]["optimum_value"]))
    best_integer_point = evaluate(root, best_integer_point)

    #Update output
    if best_integer_point == None:
        output["result"]["integer_solution"] = {}
        output["error_msg"] = "Nao foi possivel encontrar uma solucao inteira para este problema."
    else:
        output["result"]["integer_solution"] = {
            "coords": best_integer_point["coords"],
            "value": best_integer_point["value"]
        }