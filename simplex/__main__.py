import json
import os
import time
import primal_tabular
import primal_graphic

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
        match configs["method"]:
            case "GRAPHIC":
                primal_graphic.run(configs, output)
            case "TABULAR":
                primal_tabular.run(configs, output)
            case "DUAL":
                primal_tabular.run(configs, output)
            case _:
                output["error_msg"] = "Metodo invalido."
                output["status"] = 1
    except Exception as e:
        print(e)
        output["error_msg"] = "Um erro inesperado ocorreu."
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

    
    rel_path = "examples\input_sample.json" #Modify this path to test another input
    input_sample = open(os.path.join(script_dir, rel_path), "r")

    print(main(input_sample.read()))