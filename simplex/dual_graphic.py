import convertions
import primal_graphic

def run(configs, output):
    new_config = {}

    #Get the dual problem
    try:
        new_config = convertions.dual_problem(configs)
    except Exception as e:
        output["status"] = -1
        output["error_msg"] = "Unable to define the dual problem. Error: " + e.__str__()
        return
    
    primal_graphic.run(new_config, output)
