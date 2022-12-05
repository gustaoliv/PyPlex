import json
import os
import time
import primal_tabular
import primal_graphic
import dual_tabular
import dual_graphic
import integer_solution

#The main function receives a Json Object containg all inputs and configurations
def main(json_string):
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
        output["status"] = -1

    if configs["integer_solution"] and output["status"] == 0:
        try:
            integer_solution.run(configs, output)
        except Exception as e:
            output["error_msg"] = "Nao foi possivel encontrar a solucao inteira."
            output["status"] = -1

    output["ellapsed_time"] = (time.time() - start_time) * 1000

    output_json = ""
    try:
        output_json = json.dumps(output)
    except Exception as e:
        output["result"] = ""
        output["error_msg"] = "Nao foi possivel converter o resultado."
        output["status"] = 2
        output_json = json.dumps(output)

    return output_json

#The code below have no effect if you are running from another file
if __name__ == "__main__":
    script_dir = os.path.dirname(__file__).replace("simplex\\","") #<-- absolute dir the script is in

    
    rel_path = "examples\problema_radioterapico.json" #Modify this path to test another input
    input_sample = open(os.path.join(script_dir, rel_path), "r")

    print(main(input_sample.read()))