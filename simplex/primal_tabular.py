import numpy as np
import convertions

def min_pos(vec):
    index = 0
    min = vec[0]
    for i in range(1, len(vec)):
        if vec[i] < min:
            index = i
            min = vec[i]
    return index

#The simplex_primal function receives an Object containg all inputs and configurations
def run(configs, output):
    new_config = {}

    #Get the extended problem
    try:
        new_config = convertions.extended_problem(configs)
    except Exception as e:
        output["status"] = -1
        output["error_msg"] = "Unable to define the extended problem. Error: " + e
    
    iterations = []
    #Write initial state

    
    num_vars = 0
    last_iteration = {}
    while True:
        #Select in variable
        in_var = min_pos(last_iteration["z"])

        #Select out variable
        min_e = None
        min_value = float("inf")
        z = last_iteration["z"]
        for e in last_iteration["expressions"]:
            v = (z["value"] - np.dot(e, z["coeficients"])) / e[in_var]
            if v < min_value:
                min_value = v
                min_e = e
        
        #Normalize pivo line
        new_e = convertions.normalize_restriction(min_e)

        #Update system
        new_iteration = {}
        #Verify if it's optimum
        for i in range(0, num_vars):
            if z[i] > 0:
                break
        else:
            break
    
    #Write output
