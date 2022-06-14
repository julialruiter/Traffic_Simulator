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

    with open('snapshot.json', 'w') as f:
        json.dump(tm.get_snapshot(), f)

    tm.tick()

    tm.get_node_edges_in_out(2)



    