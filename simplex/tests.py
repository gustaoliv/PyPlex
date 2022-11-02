import os
import sys
import convertions
import graphic_methods
import primal_graphic
import primal_tabular

input = [
    {
        "coeficients": [1,0],
        "type": ">=",
        "value": 0
    },
    {
        "coeficients": [0,1],
        "type": ">=",
        "value": 0
    },
    {
        "coeficients": [2,1],
        "type": "<=",
        "value": 6
    },
    {
        "coeficients": [1,2],
        "type": ">=",
        "value": 6
    }
]

print("is_non_negativety_restriction test: ")
print(convertions.is_inferior_limit_restriction(input[1]))
print("")

print("extended_problem test: ")
print(convertions.extended_problem(input))
print("")

print("normalize_restriction test: ")
print(convertions.normalize_restriction(input[2], 0))
print("")

print("viability_region test: ")
print(graphic_methods.viability_region(input))
print("")