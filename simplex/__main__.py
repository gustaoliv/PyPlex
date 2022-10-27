import json
import os
import time

from core import primal_simplex

#The main function receives a Json Object containg all inputs and configurations
def main(json_string):
    configs = json.loads(json_string)

    start_time = time.time()
    output = {
        "result": {},
        "multiple_solutions": [],
        "status": 0,
        "ellapsed_time": 0,
        "error_msg": ""
    }
    try:
        match configs["method"]:
            case "PRIMAL":
                primal_simplex.run(configs)
            case _:
                output["error_msg"] = "Método inválido."
                output["status"] = -1
    except:
        output["error_msg"] = "Um erro inesperado ocorreu."
        output["status"] = -1

    output["ellapsed_time"] = (time.time() - start_time) * 1000
    return json.dumps(output)

if __name__ == "__main__":
    input_sample = open("C:/Users/mateu/OneDrive/Escola/Pesquisa Operacional/Algoritmo-simplex/tests/input_sample.json", "r")
    main(input_sample.read())
    os.system("PAUSE")