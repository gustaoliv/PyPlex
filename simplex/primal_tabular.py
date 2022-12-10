import numpy as np
from simplex import convertions

PRECISION = 3

def min(vec):
    v1 = vec["reals"]
    v2 = vec["artificials"]
    index = 0
    min = [v1[0], v2[0]]
    for i in range(1, len(v1)):
        if v2[i] < min[1] or (v2[i] == min[1] and v1[i] < min[0]):
            index = i
            min = [v1[i], v2[i]]
    return ({"real": min[0], "artificial": min[1]}, index)

def create_iteration(obj):
    iteration = {
        "z": {
            "coeficients": {
                "reals": None,
                "artificials": None
            },
            "value": {
                "real": 0.0,
                "artificial": 0.0
            }
        },
        "expressions": [],
        "base_variables": None,
        "target_point": None,
        "base_in": "",
        "base_out": "",
        "is_optimum": False
    }
    obj["iterations"].append(iteration)
    obj["iterations_count"]+=1
    return iteration

def reduce_z(index, pivo, exp):
    real_factor = -exp["coeficients"]["reals"][index]
    artificial_factor = -exp["coeficients"]["artificials"][index]
    return {
        "coeficients": 
        {
            "reals": round_list(np.array(exp["coeficients"]["reals"]) + np.array(pivo["coeficients"]) * real_factor),
            "artificials": round_list(np.array(exp["coeficients"]["artificials"]) + np.array(pivo["coeficients"]) * artificial_factor)
        },
        "value":
        {
            "real": exp["value"]["real"] + pivo["value"] * real_factor,
            "artificial": round(exp["value"]["artificial"] + pivo["value"] * artificial_factor, PRECISION)
        }
    }

def reduce_expression(index, pivo, exp):
    factor = -exp["coeficients"][index]
    return {
        "coeficients": np.array(exp["coeficients"]) + np.array(pivo["coeficients"]) * factor,
        "value": exp["value"] + pivo["value"] * factor
    }

def separe_artificial_coeficients(arr = []):
    out = {
        "reals": [],
        "artificials": []
    }
    for n in arr:
        v = str(n).split("M")
        if len(v) == 1:
            out["reals"].append(float(n))
            out["artificials"].append(0.0)
        else:
            out["reals"].append(float(v[0]) if v[0] != "" else 0)
            out["artificials"].append(float(v[1]) if v[1] != "" else 1)
    
    out["reals"] = np.array(out["reals"])
    out["artificials"] = np.array(out["artificials"])
    
    return out

def round_list(arr = [], precision = PRECISION):
    out = []
    for n in arr:
        out.append(round(n, precision))
    return out

def get_z_text(r = 0, a = 0):
    out = ""
    r = round(r,PRECISION)
    a = round(a,PRECISION)
    if(r != 0):
        out += str(r)
    if(a != 0):
        out += " "+str(a)+"M" if a < 0 else "+ " + str(a) + "M"
    if out == "":
        out = "0"
    return out

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    new_config = {}

    #Get the extended problem
    try:
        new_config = convertions.extended_problem(configs)
    except Exception as e:
        output["status"] = -1
        output["error_msg"] = "Unable to define the extended problem. Error: " + e.__str__()
        return
    
    #Write initial state
    result = {
        "optimum_point": None,
        "optimum_value": 0,
        "iterations": [],
        "iterations_count": 0,
        "variables": new_config["variables"],
        "input_variables": new_config["input_variables"],
        "slack_variables": new_config["slack_variables"],
        "artificial_variables": new_config["artificial_variables"]
    }
    current_iteration = create_iteration(result)
    current_iteration["z"]["coeficients"] = separe_artificial_coeficients( np.array(new_config["objective_function"]))
    current_iteration["z"]["coeficients"]["reals"] *= -1 if new_config["objective"] == "MAXIMIZE" else 1
    current_iteration["z"]["value"] = {"real": 0.0, "artificial": 0.0}
    current_iteration["base_variables"] = []
    num_of_vars = len(result["variables"])
    
    i = 0
    for r in new_config["restrictions"]:
        #Ignore lower_bound_limits (temporary)
        if(convertions.is_inferior_limit_restriction(r)):
            continue
        
        item = {
            "coeficients": np.array(r["coeficients"]),
            "value": r["value"],
            "base": ""
        }
        for s in result["slack_variables"]:
            if item["coeficients"][result["variables"].index(s)] == 1:
                item["base"] = s
                break
        for a in result["artificial_variables"]:
            if item["coeficients"][result["variables"].index(a)] == 1:
                item["base"] = a
                break

        current_iteration["expressions"].append(item)
        current_iteration["base_variables"].append(item["base"])
        i+=1
    
    #Handle artificial variables
    for a in result["artificial_variables"]:
        i = result["variables"].index(a)
        for e in current_iteration["expressions"]:
            if(e["coeficients"][i] == 1):
                current_iteration["z"]["coeficients"]["artificials"] -= e["coeficients"]
                current_iteration["z"]["coeficients"]["artificials"][i] = 0.0
                current_iteration["z"]["value"]["artificial"] -= e["value"]
                e["base"] = a
                break

    #Process objective function coeficients to define the bounds of each one 
    sign_relation = np.zeros(num_of_vars)
    for r in new_config["restrictions"]:
        if convertions.is_inferior_limit_restriction(r):
            i = r["coeficients"].tolist().index(1)
            if r["type"] == ">=":
                sign_relation[i] = 1    #This coeficient must be >= 0
            elif r["type"] == "<=":
                sign_relation[i] = -1   #This coeficient must be <= 0
            else:
                sign_relation[i] = 0    #This coeficient can be anything

    #Start the loop process
    k = 0 #Temp
    changed_variables = []
    while True and k < 10:
        k+=1

        #Try get target point
        coeficients = []
        values = []
        for e in current_iteration["expressions"]:
            coeficients.append(e["coeficients"])
            values.append(e["value"])

        #Apply 0 to the non-basic variables
        for i in range(0, num_of_vars):
            x = result["variables"][i]
            if current_iteration["base_variables"].__contains__(x):
                continue
            v = np.zeros(num_of_vars)
            v[i] = 1
            coeficients.append(v)
            values.append(0)
        
        try:
            current_iteration["target_point"] = np.linalg.solve(np.array(coeficients), np.array(values))
        except Exception as e:
            #The intersection is a line or it doesn't exists
            print("Couldn't solve the problem.")
        
        #Select the in variable
        base_in_value = {}
        base_in_index = {}
        for i in range(0, num_of_vars):
            real = current_iteration["z"]["coeficients"]["reals"][i]
            artf = current_iteration["z"]["coeficients"]["artificials"][i]
            match sign_relation[i]:
                case 1:
                    break
                case -1:
                    break
                case 0:
                    break
        
        (base_in_value, base_in_index) = min(current_iteration["z"]["coeficients"])
        
        #Verify if it's optimum
        if base_in_value["artificial"] > 0 or (base_in_value["artificial"] == 0 and base_in_value["real"] >= 0):
            result["optimum_point"] = current_iteration["target_point"].tolist()
            result["optimum_value"] = current_iteration["z"]["value"]
            current_iteration["is_optimum"] = True
            break
        
        current_iteration["base_in"] = result["variables"][base_in_index]

        #Select out variable
        min_v = float("inf")
        target_index = None
        base_out = None
        while(True):
            for i in range(0, len(current_iteration["expressions"])):
                e = current_iteration["expressions"][i]
                n = e["coeficients"][base_in_index]
                v = abs(e["value"] / n) if n != 0 else float("inf")
                if(v <= min_v and not changed_variables.__contains__(e["base"])):
                    min_v = v
                    target_index = i
                    base_out = e["base"]
            if target_index == None:
                changed_variables = []
            else:
                break

        changed_variables.append(current_iteration["base_in"])
        current_iteration["base_out"] = base_out
        
        #Normalize pivo line
        pivo = convertions.normalize_restriction(current_iteration["expressions"][target_index], base_in_index)
        pivo["base"] = current_iteration["base_in"]

        #Update system
        next_iteration = create_iteration(result)
        next_iteration["z"] = reduce_z(base_in_index, pivo, current_iteration["z"])
        next_iteration["base_variables"] = list(map(lambda a : 
                                                current_iteration["base_in"] if a == current_iteration["base_out"] 
                                                else a, current_iteration["base_variables"]))

        for e in current_iteration["expressions"]:
            if e["base"] == current_iteration["base_out"]:
                next_iteration["expressions"].append(pivo)
            else:
                new_e = reduce_expression(base_in_index, pivo, e)
                new_e["base"] = e["base"]
                next_iteration["expressions"].append(new_e)
            
        current_iteration = next_iteration
    
    #Write output
    result["optimum_point"] = round_list(result["optimum_point"])
    result["optimum_value"] = get_z_text(result["optimum_value"]["real"], result["optimum_value"]["artificial"])
    for iteration in result["iterations"]:
        iteration["target_point"] = round_list(iteration["target_point"])

        aux = []
        c = iteration["z"]["coeficients"]
        for i in range(0,len(c["reals"])):
            txt = get_z_text(c["reals"][i], c["artificials"][i])
            aux.append(txt)
        iteration["z"]["coeficients"] = aux
        iteration["z"]["value"] = get_z_text(iteration["z"]["value"]["real"], iteration["z"]["value"]["artificial"])

        for exp in iteration["expressions"]:
            exp["coeficients"] = round_list(exp["coeficients"])
            exp["value"] = round(exp["value"], PRECISION)
                
    output["result"] = result
    return output