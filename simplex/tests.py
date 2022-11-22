import os
import sys
import convertions
import graphic_methods
import primal_graphic
import primal_tabular

input = {
    "method": "GRAPHIC",
    "objective": "MAXIMIZE",
    "objective_function": [3, 2],
    "restrictions": [
        {
            "coeficients": [2,1],
            "type": "<=",
            "value": 6
        },
        {
            "coeficients": [1,2],
            "type": "<=",
            "value": 6
        },
        {
            "coeficients": [1,0],
            "type": ">=",
            "value": 0
        },
        {
            "coeficients": [0,1],
            "type": ">=",
            "value": 0
        }
    ],
    "variable_names": ["x1", "x2"],
    "integer_solution": False
}

test_list = [3,4]

for n in test_list:
    match n:
        case 0:
            print("is_non_negativety_restriction test: ")
            print(convertions.is_inferior_limit_restriction(input["restrictions"][1]))
            print("")
        case 1:
            print("extended_problem test: ")
            print(convertions.extended_problem(input))
            print("")
        case 2:
            print("normalize_restriction test: ")
            print(convertions.normalize_restriction(input["restrictions"][2], 0))
            print("")
        case 3:
            print("viability_region test: ")
            out = graphic_methods.viability_region(input)
            print(len(out[0]))
            print("")
        case 4:
            print("viability_region in extended_problem test: ")
            out = graphic_methods.viability_region(convertions.extended_problem(input))
            print(len(out[0]))
            print("")
        case _:
            print(" test: ")
            print("")