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

    tm = TrafficManager(network_config)
    with open('snapshot.json', 'w') as f:
        json.dump(tm.get_snapshot(), f)



    