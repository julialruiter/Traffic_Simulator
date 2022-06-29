from traffic_network import Network
import copy

class TrafficManager:
    def __init__(self, network_config) -> None:
        '''Establishes an instance of TrafficManager to run on the given network structure.
        Attributes:
            graph:  Network object that the TrafficManager runs on.
            timestamp:  Simulation timestamp.
        '''
        self.graph = Network(self, network_config)
        self.timestamp = 0
        
    
    def tick(self):
        '''API function:  advance state of network by one unit of time.
        '''
        self.timestamp += 1  
        steps_count = 0

        expended_energy = 0                       # work actually done
        sum_maximum_expendible_energy = 0         # maximum work possible
        energy_used_percent = 0

        while True:
            steps_count += 1

            network_tick_outputs = self.graph.tick()
            expended_energy += network_tick_outputs[0]
            sum_maximum_expendible_energy += network_tick_outputs[1]
            if not network_tick_outputs[0]:
                # no more movement possible
                break            

        print("Steps needed to process tick: ", steps_count)
        self.graph.restore_tick_potential()      # refresh for next tick

        if sum_maximum_expendible_energy != 0:
            energy_used_percent = expended_energy / sum_maximum_expendible_energy
        else:
            energy_used_percent = None 
        print("Percent of available energy used on tick: ", energy_used_percent*100, "%")
        return energy_used_percent
              

    def get_snapshot(self):
        '''API function:  outputs list of nodes, edge attributes, car attributes.
        Output is formatted in such a way that it can be used as input for a new simulation.
        '''
        raw = copy.deepcopy(self.__dict__)
        raw_graph = raw["graph"]
        nodes =  raw_graph.__dict__.pop("node_ID_to_node", None)
        edges =  raw_graph.__dict__.pop("edge_ID_to_edge", None)
        new = {}
        new["nodes"] = [k for k in nodes.keys()]
        new["edges"] = [k for k in edges.keys()]
        network_raw = self.graph.get_snapshot()
        return network_raw


    def get_snapshot_deltas(self):
        '''API function:  list of changes from previous state.  
        Will be created in future versions.
        '''
        pass  

    def get_timestamp(self):
        '''API function:  returns (sequential) state number.
        '''
        return self.timestamp  


    def get_node_edges_in_out(self, node_ID):  
        '''API function:  lists the IDs of inbound and outbound edges for a particular node.
        This information can also be found via 'get_snapshot()'.
        '''
        node = self.graph.get_node_from_id(node_ID)
        inbound_edge_list = list(node.get_node_inbound())
        outbound_edge_list = list(node.get_node_outbound())
        node_output = {}
        node_output["node_id"] = node_ID
        node_output["inbound_edges"] = inbound_edge_list
        node_output["outbound_edges"] = outbound_edge_list


    def add_car(self, car):
        '''API function:  place car (dictionary object) onto the network's waiting queue.
        Please note that the current iteration of add_car only supports placement directly onto Edges (identified by "start_edge").
        '''
        if self.graph.check_valid_car(car) == True:
            self.graph.add_car(car)

    def remove_car(self, car_id):
        '''API function:  removes the Car associated with 'car_id' from the simulation.
        This is done by forcing it into Car.status = 'Removed from simulation'.
        '''
        if not car_id in self.graph.car_ID_to_car:
            raise Exception("There is no car associated with this ID.")

        car_object = self.graph.car_ID_to_car[car_id]
        car_edge_ID = car_object.get_current_edge()
        car_edge = self.graph.edge_ID_to_edge[car_edge_ID]

        car_object.route_status = 'Removed from simulation at tick #' + str(self.get_timestamp())
        car_edge.completed_cars.append(car_id)

        car_edge.current_cars.remove(car_object)
        car_edge.edge_car_ID_to_car.pop(car_id) 


    def pause_car(self, car_id):
        '''API function:  forefully halts the Car associated with 'car_id' until a 'resume_car' call is received.
        No cars behind it may pass.
        '''
        if not car_id in self.graph.car_ID_to_car:
            raise Exception("There is no car associated with this ID.")

        car_object = self.graph.car_ID_to_car[car_id]
        car_object.set_mobility(False)
        car_object.route_status = 'Paused'        

    def resume_car(self, car_id):
        '''API function:  allows the Car associated with 'car_id' to resume moving.
        '''
        if not car_id in self.graph.car_ID_to_car:
            raise Exception("There is no car associated with this ID.")
            
        car_object = self.graph.car_ID_to_car[car_id]
        car_object.set_mobility(True)
        car_object.route_status = 'In progress'

    def get_all_paths_A_to_B(self, start_edge_ID, end_edge_ID):
        '''API function:  Given a start and end Edge id, return a list of all valid paths that do not repeat Edges.
        '''
        return self.graph.all_paths_depth_first_search(self, start_edge_ID, end_edge_ID, [], [])

    def get_path_distance(self, path):
        '''API function:  Given the ordered list of Edges as "path", evaluate the total distance it would take to travel.
        This function assumes that the entirety of each Edge is traveled.
        '''
        return self.graph.path_cost_distance(self, path)

    def get_path_minimum_time(self, path):
        '''API function:  Given the ordered list of Edges as "path", evaluate the the minimum time it would take to travel (in ticks) given each Edge's speed limit.
        Minimum time is calculated assuming a car is able to travel the maximum speed per edge unencumbered.
        This function assumes that the entirety of each Edge is traveled and includes any Node-crossing time penalties.
        Note:  time cost does NOT include Node-crossing time out of the final edge as the Car is expected to exit the Network before the Edge's end.
        '''
        return self.graph.path_cost_minimum_time(self, path)

    def get_shortest_path_A_to_B(self, all_paths_list):
        '''API function:  Given all_paths_list (a list of paths from A to B as calculated using self.get_all_paths_A_to_B()),
        returns the path with the shortest total distance in terms of length.
        '''
        return self.graph.choose_path(self, all_paths_list, "Shortest")

    def get_theoretical_fastest_path_A_to_B(self, all_paths_list):
        '''API function:  Given all_paths_list (a list of paths from A to B as calculated using self.get_all_paths_A_to_B()),
        returns the path with the minimum total travel time (assuming no congestion).
        '''
        return self.graph.choose_path(self, all_paths_list, "Fastest")