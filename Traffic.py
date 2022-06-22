from traffic_network import Network
import copy

class TrafficManager:
    def __init__(self, network_config) -> None:
        '''Establishes an instance of TrafficManager to run on the given network structure.
        Attributes:
            graph:  Network object that the TrafficManager runs on.
            timestamp:  Simulation timestamp.
        '''
        self.graph = Network(network_config)
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
        print("Percent of available energy used on tick: ", energy_used_percent)
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
        '''API function:  returns (sequantial) state number.
        '''
        return self.timestamp  

    def get_node_edges_in_out(self, node_ID):  
        '''API function:  lists the IDs of inbound and outbound edges for a particular node.
        '''
        node = self.graph.get_node_from_id(node_ID)
        inbound_edge_list = list(node.get_node_inbound())
        outbound_edge_list = list(node.get_node_outbound())
        node_output = {}
        node_output["node_id"] = node_ID
        node_output["inbound_edges"] = inbound_edge_list
        node_output["outbound_edges"] = outbound_edge_list
        # print(node_output)

    def add_car(self, car):
        '''API function:  place car (dictionary object) onto the network's waiting queue.
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