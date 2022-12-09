import pdb


def treat_restrictions(restrictions, num_variables):
    restrictions_list = []

    current_restriction = []
    for i in range(0, len(restrictions)):
        current_restriction.append(restrictions[i])
        if len(current_restriction) == num_variables + 2:
            restrictions_list.append({
                "coeficients": [float(val) for val in current_restriction[:-2]],
                "type": current_restriction[-2],
                "value": float(current_restriction[-1])
            })

            current_restriction = []

    for i in range(int(num_variables)):
        current_restriction = list(range(int(num_variables)))
        current_restriction = [x * 0 for x in current_restriction]
        current_restriction[i] = 1
        restrictions_list.append({
            "coeficients": current_restriction,
            "type": ">=",
            "value": 0
        })

    return restrictions_list


def make_json(session_dict):
    restr = []
    funcObj = []
    for k, v in session_dict.items():
        if k == 'numVar' or k == 'numRest' or k == 'method' or k == 'objective' or k == "exibition_type" or k == 'integer_solution':
            continue

        if 'a' in str(k):
            restr.append(v)
        else:
            funcObj.append(float(v))

    restrictions = treat_restrictions(restr, int(session_dict["numVar"]))

    requestJson = {
        "problem_type": session_dict["method"],
        "method": session_dict["exibition_type"],
        "objective": session_dict["objective"],
        "objective_function": funcObj,
        "restrictions": restrictions,
    }

    if "integer_solution" in session_dict.keys():
        requestJson["integer_solution"] = True
    else:
        requestJson["integer_solution"] = False

    var_names = []
    for i in range(1, int(session_dict["numVar"]) + 1):
        var_names.append(f"x{i}")

    requestJson["variable_names"] = var_names

    return requestJson


def mmc(nums):
    max_ = max(nums)
    i = 1
    while True:
        mult = max_ * i
        if all(mult%nr == 0 for nr in nums):
            return mult
        i += 1