import numpy as np

PRECISION = 3

def round_list(arr = []):
    out = []
    for n in arr:
        out.append(round(n, PRECISION))
    return out

def extended_problem(configs = {}):
    output = configs.copy()

    if len(output["restrictions"]) < 3:
        return None

    ref = []
    res = []
    #Separe inferior limit and normal restrictions
    for r in output["restrictions"]:
        if is_inferior_limit_restriction(r):
            new_r = r.copy()
            new_r["is_lower_bound_restriction"] = True
            res.append(new_r)
        else:
            ref.append(r.copy())
    
    #Count the number of adicional variables
    slack_vars = 0
    virtual_vars = 0
    for restriction in ref:
        c = restriction["coeficients"]
        
        if ["<=", ">="].count(restriction["type"]): slack_vars+=1
        if ["=", ">="].count(restriction["type"]): virtual_vars+=1

    adicional_vars = slack_vars + virtual_vars

    #Update the restriction coeficients
    length = len(ref[0]["coeficients"])
    for r in res:
        r["coeficients"] = np.array(concat(r["coeficients"], np.zeros(adicional_vars)))
    
    #Update the objective function coeficients
    output["objective_function"] = concat(output["objective_function"], np.zeros(adicional_vars))

    #Insert new inferior limits
    total_length = length + adicional_vars
    for i in range(length, total_length):
        c = np.zeros(total_length)
        c[i] = 1
        res.append({"coeficients": c, "type":">=", "value": 0, "is_lower_bound_restriction": True})

    s_names = []
    a_names = []
    output["variables"] = output["variable_names"].copy()
    pos = length
    for r in ref:
        c = np.array(concat(r["coeficients"], np.zeros(adicional_vars)))
        
        if ["<=", ">="].count(r["type"]):
            c[pos] = 1 if r["type"] == "<=" else -1
            pos+=1
            name = "sx"+pos.__str__()
            s_names.append(name)
            output["variables"].append(name)
        
        if ["=", ">="].count(r["type"]):
            c[pos] = 1
            output["objective_function"][pos] = "M"
            pos+=1
            name = "ax"+pos.__str__()
            a_names.append(name)
            output["variables"].append(name)

        res.append({"coeficients": c, "type":"=", "value": r["value"]})
    
    output["input_variables"] = output["variable_names"]
    output["slack_variables"] = s_names
    output["artificial_variables"] = a_names
    output["restrictions"] = res
    output["extended_problem"] = True
    
    return output

def normalize_restriction(restriction, ref_index):
    r = restriction.copy()
    c = np.array(r["coeficients"])
    ref_value = c[ref_index]
    c = c / ref_value
    r["coeficients"] = c.tolist()
    r["value"] /= ref_value
    return r

def dual_problem(configs = {}):
    output = configs.copy()
    output["objective"] = "MAXIMIZE"
    output["objective_function"] = []
    output["problem_type"] = "DUAL"
    output["restrictions"] = []
    output["variable_names"] = []

    exp = []
    for r in configs["restrictions"]:
        if not is_inferior_limit_restriction(r):
            exp.append(r)
    
    num_vars = len(configs["objective_function"])
    for i in range(0, num_vars):
        c = {
            "coeficients": [],
            "type": "<=",
            "value": configs["objective_function"][i]
        }
        output["restrictions"].append(c)
        for r in exp:
            c["coeficients"].append(r["coeficients"][i])
    
    num_res = len(exp)
    for i in range(0, num_res):
        r = configs["restrictions"][i]

        if r["type"] != "=":
            c = {
                "coeficients": np.zeros(num_res),
                "type": ">=",
                "value": 0
            }
            c["coeficients"][i] = 1
            output["restrictions"].append(c)
        
        output["variable_names"].append("y"+str(i+1))
        output["objective_function"].append(r["value"])

    return output

def concat(arr1 = [], arr2 = []):
    (l1, l2) = (len(arr1), len(arr2))
    out = [0] * (l1 + l2)
    for i in range(0, l1):
        out[i] = arr1[i]
    for i in range(0, l2):
        out[l1 + i] = arr2[i]
    return out

def is_inferior_limit_restriction(restriction):
    var_index = -1
    c = restriction["coeficients"]
    for i in range(0, len(c)):
        if c[i] == 1:
            if var_index != 1:
                var_index = i
            else:
                return False
        elif c[i] != 0:
            return False
    
    return restriction["type"] == ">="