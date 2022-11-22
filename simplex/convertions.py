import numpy as np

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
        slack_vars+=1
        if restriction["type"] == ">=": virtual_vars+=1

    adicional_vars = slack_vars + virtual_vars

    #Update the restriction coeficients
    length = len(ref[0]["coeficients"])
    for r in res:
        r["coeficients"] = r["coeficients"].__add__(np.zeros(adicional_vars).tolist())
    
    #Update the objective function coeficients
    output["objective_function"] = output["objective_function"].copy().__add__(np.zeros(adicional_vars).tolist())

    #Insert new inferior limits
    total_length = length + adicional_vars
    for i in range(length, total_length):
        c = np.zeros(total_length)
        c[i] = 1
        res.append({"coeficients": c, "type":">=", "value": 0, "is_lower_bound_restriction": True})

    s_names = []
    a_names = []
    s_pos = length
    a_pos = length + slack_vars
    for r in ref:
        c = r["coeficients"].__add__(np.zeros(adicional_vars).tolist())

        c[s_pos] = 1
        s_pos+=1
        s_names.append("sx"+s_pos.__str__())

        if r["type"] == ">=":
            c[a_pos+1] = "M"
            a_pos+=1
            a_names.append("ax"+a_pos.__str__())

        res.append({"coeficients": c, "type":"=", "value": r["value"]})
    
    output["variable_names_extended"] = output["variable_names"] + s_names + a_names
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

def primal_to_dual(configs = {}):
    output = []
    return output

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