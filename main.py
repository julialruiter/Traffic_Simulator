from Traffic import TrafficManager
from configs.UnderlyingNetworkGenerator import NetworkGenerator
import json

if __name__ == "__main__":
    network_config = None
    try:
        with open("./configs/output_as_input_example.json") as json_file:   # need fully qualified path, not relative
            network_config = json.load(json_file)
            # print(network_config)
    except Exception as E:
        print(E)

    network_config["car_list"] = network_config.pop("current_cars", None)
    network_config["car_list"] += network_config.pop("completed_cars", None)
    
    car_config = network_config["car_list"]
    print(car_config)
    # car_config = None
    # try:
    #     with open("./configs/output_as_input_example.json") as car_file:   # need fully qualified path, not relative
    #         car_config = json.load(car_file)
    # except Exception as E:
    #     print(E)

    # node_DEFAULTS = None
    # try:
    #     with open("./configs/DEFAULT_node_values_config.json") as node_defaults:   # need fully qualified path, not relative
    #         node_DEFAULTS = json.load(node_defaults)
    # except:
    #     print("Node value defaults configuration file is missing.") 


    tm = TrafficManager(network_config)

    for car in car_config:
        tm.add_car(car)

    # for car in car_config["car_list"]:
    #     tm.add_car(car)
    
    for tick in range(4):
        tm.tick()
        #print("Network Congestion" , tm.tick())
        with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
            json.dump(tm.get_snapshot(), f)
    
    tm.pause_car(7000)

    for tick in range(2):
        tm.tick()
        #print("Network Congestion" , tm.tick())
        with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
            json.dump(tm.get_snapshot(), f)
    
    tm.resume_car(7000)

    for tick in range(2):
        tm.tick()
        #print("Network Congestion" , tm.tick())
        with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
            json.dump(tm.get_snapshot(), f)

    # # tm.remove_car(7000)

    # tm.tick()
    # with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
    #         json.dump(tm.get_snapshot(), f)



    # ng = NetworkGenerator()
    # print(ng.generate_complete_bidirectional_network_default_values(5))


    