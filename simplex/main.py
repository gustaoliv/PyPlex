import json
import os
import time
from simplex import primal_tabular
from simplex import primal_graphic
from simplex import dual_tabular
from simplex import dual_graphic
from simplex import integer_solution


#The main function receives a Json Object containg all inputs and configurations
def solve_simplex(json_string):
    configs = json.loads(json_string)

    start_time = time.time()
    output = {
        "result": {},
        "status": 0,
        "ellapsed_time": 0,
        "error_msg": ""
    }
    try:
        match (configs["problem_type"] + " - " + configs["method"]):
            case "PRIMAL - GRAPHIC":
                primal_graphic.run(configs, output)
            case "PRIMAL - TABULAR":
                primal_tabular.run(configs, output)
            case "DUAL - GRAPHIC":
                dual_graphic.run(configs, output)
            case "DUAL - TABULAR":
                dual_tabular.run(configs, output)
            case _:
                output["error_msg"] = "Metodo ou tipo invalido."
                output["status"] = 1
    except Exception as e:
        output["error_msg"] = "Um erro inesperado ocorreu: " + e.__str__()
        output["status"] = 2

    if configs["integer_solution"] and output["status"] == 0:
        try:
            integer_solution.run(configs, output)
        except Exception as e:
            output["error_msg"] = "Nao foi possivel encontrar a solucao inteira. Erro: " + str(e)
            output["status"] = 3

    output["ellapsed_time"] = (time.time() - start_time) * 1000

    output_json = ""
    try:
        output_json = json.dumps(output)
    except Exception as e:
        output["result"] = ""
        output["error_msg"] = "Nao foi possivel converter o resultado."
        output["status"] = 4
        output_json = json.dumps(output)

    return output_json

#The code below have no effect if you are running from another file
if __name__ == "__main__":
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

    
    rel_path = "examples\ex004.json" #Modify this path to test another input
    input_sample = open(os.path.join(script_dir, rel_path), "r")

    print(solve_simplex(input_sample.read()))