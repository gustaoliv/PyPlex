import numpy as np
import convertions
import graphic_methods

def min(vec):
    index = 0
    min = vec[0]
    for i in range(1, len(vec)):
        if vec[i] < min:
            index = i
            min = vec[i]
    return (min, index)

def create_iteration(obj):
    iteration = {
        "z": {
            "coeficients": None,
            "value": 0
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

def reduce_expression(index, pivo, exp):
    factor = -exp["coeficients"][index]
    return {
        "coeficients": np.array(exp["coeficients"]) + np.array(pivo["coeficients"]) * factor,
        "value": exp["value"] + pivo["value"] * factor
    }

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    new_config = {}

    #Get the extended problem
    try:
        new_config = convertions.extended_problem(configs)
    except Exception as e:
        output["status"] = -1
        output["error_msg"] = "Unable to define the extended problem. Error: " + e
    
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
    current_iteration["z"]["coeficients"] = np.array(new_config["objective_function"]) * (-1)
    current_iteration["base_variables"] = result["slack_variables"]
    i = 0
    for r in new_config["restrictions"]:
        #Ignore lower_bound_limits (temporary)
        if(convertions.is_inferior_limit_restriction(r)):
            continue

        current_iteration["expressions"].append(
            {
                "coeficients": np.array(r["coeficients"]),
                "value": r["value"],
                "base": result["slack_variables"][i]
            })
        i+=1
    
    #Handle artificial variables

    #Start the loop process
    num_of_vars = len(result["variables"])
    k = 0 #Temp
    while True and k < 10:
        k+=1

        #Try get target point
        coeficients = []
        values = []
        for e in current_iteration["expressions"]:
            coeficients.append(e["coeficients"])
            values.append(e["value"])

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
        
        #Select in variable
        (min_value, base_in_index) = min(current_iteration["z"]["coeficients"])
        
        #Verify if it's optimum
        if min_value >= 0:
            result["optimum_point"] = current_iteration["target_point"].tolist()
            result["optimum_value"] = current_iteration["z"]["value"]
            current_iteration["is_optimum"] = True
            break
        
        current_iteration["base_in"] = result["variables"][base_in_index]

        #Select out variable
        min_v = float("inf")
        target_index = None
        base_out = None
        for i in range(0, len(current_iteration["expressions"])):
            e = current_iteration["expressions"][i]
            v = e["value"] / e["coeficients"][base_in_index]
            if(v < min_v):
                min_v = v
                target_index = i
                base_out = e["base"]
        current_iteration["base_out"] = base_out
        
        #Normalize pivo line
        pivo = convertions.normalize_restriction(current_iteration["expressions"][target_index], base_in_index)
        pivo["base"] = current_iteration["base_in"]

        #Update system
        next_iteration = create_iteration(result)
        next_iteration["z"] = reduce_expression(base_in_index, pivo, current_iteration["z"])
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
    
    for iteration in result["iterations"]:
        iteration["target_point"] = iteration["target_point"].tolist()
        iteration["z"]["coeficients"] = iteration["z"]["coeficients"].tolist()
        for exp in iteration["expressions"]:
            c = exp["coeficients"]
            if isinstance(c, np.ndarray):
                exp["coeficients"] = c.tolist()

    output["result"] = result
    return output
