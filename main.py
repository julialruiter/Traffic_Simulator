from Traffic import TrafficManager
import json

if __name__ == "__main__":
    network_config = None
    try:
        with open("./configs/network_config.json") as json_file:   # need fully qualified path, not relative
            network_config = json.load(json_file)
            # print(network_config)
    except Exception as E:
        print(E)

    car_config = None
    try:
        with open("./configs/car_config.json") as car_file:   # need fully qualified path, not relative
            car_config = json.load(car_file)
    except Exception as E:
        print(E)

    tm = TrafficManager(network_config)

    for car in car_config["car_list"]:
        tm.add_car(car)

    # count = 0
    # while True:
    #     count+=1
    #     network_potential = tm.tick()
    #     with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
    #         json.dump(tm.get_snapshot(), f)
    #     if network_potential:
    #         print("Iteration: #", count, "\t Potential:", network_potential)
    #     else:
    #         print("Iteration: #", count, "\t Potential:", network_potential)
    #         break
    
    for tick in range(6):
        tm.tick()
        #print("Network Congestion" , tm.tick())
        with open(str(tm.get_timestamp()) + '_snapshot.json', 'w') as f:
            json.dump(tm.get_snapshot(), f)



    # tm.get_node_edges_in_out(2)




    