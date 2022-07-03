from network_cars import Car

import collections
import copy
import random
from cmath import inf
import json

class Network:
    def __init__(self, TrafficManagerPointer, config) -> None:
        '''Contains all functions and attributes pertaining to the (road) network as a whole.
        Attributes:
            TrafficManager_pointer:  Identifies which TrafficManger simulation is associated with this network
            node_ID_to_node:  Dictionary mapping Node IDs to Node objects.
            edge_ID_to_edge:  Dictionary mapping Edge IDs to Edge objects.
            car_ID_to_car:  Dictionary mapping Car IDs to Car objects.
            global_tick:  Tick index, aligns with TrafficManager tick
        '''
        self.TrafficManager_pointer = TrafficManagerPointer
        self.node_ID_to_node = collections.defaultdict(lambda: None)
        self.edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.car_ID_to_car = collections.defaultdict(lambda: None)
        self.edge_default_config = {}
        self.node_default_config = {}
        self.car_default_config = {}
        self.global_tick = 0

        # load edge default config
        try:
            with open("./configs/DEFAULT_edge_values_config.json") as edge_defaults:   # need fully qualified path, not relative
                self.edge_default_config = json.load(edge_defaults)
        except:
            print("Edge value defaults configuration file is missing.")

        # load node default config
        try:
            with open("./configs/DEFAULT_node_values_config.json") as node_defaults:   # need fully qualified path, not relative
                self.node_default_config = json.load(node_defaults)
        except:
            print("Node value defaults configuration file is missing.")    

        # load car default config
        try:
            with open("./configs/DEFAULT_car_values_config.json") as car_defaults:   # need fully qualified path, not relative
                self.car_default_config = json.load(car_defaults)
        except:
            print("No Car object defaults have been given.  May raise errors if incomplete Car objects are added to the Network.")  


        # create dictionaries mapping Node and Edge objects to Network
        for node in config["node_list"]:
            self.add_node(node)
        for edge in config["edge_list"]:
            self.add_edge(edge)

    def get_Network_pointer(self):
        '''Returns tick index (which aligns with TrafficManager tick).
        '''
        return self.global_tick
    
    def get_global_tick(self):
        '''Returns a pointer to this Network instance.
        Useful for directly generating cars OR keeping track managing multiple simulations at once.
        '''
        return self.global_tick

    def get_snapshot(self):
        '''Outputs dictionary containing snapshot data for all nodes and edges in the network.
        '''
        car_set = set()
        completed_car_set = set()
        snapshot = {}

        edge_snapshots = []
        for edge_key in self.edge_ID_to_edge:
            edge = self.edge_ID_to_edge[edge_key]
            edge_raw = edge.get_snapshot()
            for car_id in edge_raw["current_cars"]:  
                car_set.add(car_id)
            for car_id in edge_raw["completed_cars"]:  
                completed_car_set.add(car_id)
            edge_snapshots.append(edge_raw)
        snapshot["edges"] = edge_snapshots

        node_snapshots = []
        for node_key in self.node_ID_to_node:
            node = self.node_ID_to_node[node_key]
            node_raw = node.get_snapshot()  
            node_snapshots.append(node_raw)
        snapshot["nodes"] = node_snapshots

        car_snapshots_current = []
        car_snapshots_completed = []
        for car_id in car_set:   # cars on edge
            car = self.car_ID_to_car[car_id]
            car_raw = car.get_snapshot()
            car_snapshots_current.append(car_raw)
        for car_id in completed_car_set:    # cars that completed their route on this edge
            car = self.car_ID_to_car[car_id]
            car_raw = car.get_snapshot()
            car_snapshots_completed.append(car_raw)
        snapshot["current_cars"] = car_snapshots_current
        snapshot["completed_cars"] = car_snapshots_completed
        return snapshot


    def add_node(self, node):
        '''Imports node(s) from given node dictionary and adds them to the network.
        '''
        # check if values exist in config, else assign defaults
        if "intersection_time_cost" in node:
            intersection_cost = node["intersection_time_cost"]
        else:
            intersection_cost = self.node_default_config["intersection_time_cost"]

        if "stoplight_pattern" in node:
            stoplight_pattern = node["stoplight_pattern"]
        else:
            stoplight_pattern = None
        
        if "stoplight_duration" in node:
            stoplight_duration = node["stoplight_duration"]
        else:
            stoplight_duration = self.node_default_config["stoplight_duration"]

        if "stoplight_delay" in node:
            stoplight_delay = node["stoplight_delay"]
        else:
            stoplight_delay = self.node_default_config["stoplight_delay"]

        # create new Node object
        new_node = Node(self,                    # adds Network reference
                        node["id"], 
                        intersection_cost,
                        stoplight_pattern,
                        stoplight_duration,
                        stoplight_delay) 
        if self.node_ID_to_node[new_node.get_node_ID()]:
            raise Exception("There is already a Node with this ID")
        self.node_ID_to_node[new_node.get_node_ID()] = new_node


    def add_edge(self, edge):
        '''Imports edge(s) from given edge dictionary.
        If both the start and end nodes are already in the network, then the edge will be added.
        Any Edge attribute values not given in the edge object (imported) will instead be assigned from the imported defaults file: edge_default_config.
        Note:  there are no default values for id, start_node_id, nor end_node_id as these are an Edge's unique identifiers.
        '''
        # check if values exist in config, else assign defaults
        if "edge_length" in edge:
            edge_length = edge["edge_length"]
        else:
            edge_length = self.edge_default_config["edge_length"]

        if "max_speed" in edge:
            speed_limit = edge["max_speed"]
        else:
            speed_limit = self.edge_default_config["max_speed"]

        if "max_capacity" in edge:
            max_capacity = edge["max_capacity"]
        else:
            max_capacity = self.edge_default_config["max_capacity"]
            if max_capacity == 'Infinity':
                max_capacity = inf
                print(max_capacity)

        # create new Edge object
        new_edge = Edge(edge["id"],
                        edge["start_node"],
                        edge["end_node"],
                        edge_length,
                        speed_limit,
                        max_capacity)

        if new_edge.get_start_node_id() in self.node_ID_to_node:
            if new_edge.get_end_node_id() in self.node_ID_to_node:
                start_node = self.node_ID_to_node[new_edge.get_start_node_id()]
                new_edge.set_start_node(start_node)
                start_node.add_to_outbound(new_edge)

                end_node = self.node_ID_to_node[new_edge.get_end_node_id()]
                new_edge.set_end_node(end_node)
                end_node.add_to_inbound(new_edge)

                self.edge_ID_to_edge[new_edge.get_edge_ID()] = new_edge
            else:
                raise Exception("End Node ID is not part of the network.")
        else:
            raise Exception("Start Node ID is not part of the network.")

    def add_car(self, car):
        '''Places Car (object) on the waiting queue for its specified start_edge.
        Validity checks have been passed up to the TrafficManager level as a part of "add_car(car)",
        ensuring that any Cars received are valid OR can be made valid using the DEFAULT_car_values_config.json file.
        '''
        # check if values exist in config, else assign defaults
        if "start_pos_meter" in car:
            start_pos_meter = car["start_pos_meter"]
        else:    # default to edge start
            start_pos_meter = 0

        if "end_pos_meter" in car:
            end_pos_meter = car["end_pos_meter"]
        else:    # default to edge end
            end_edge_ID = car["end_edge"]
            end_edge_object = self.edge_ID_to_edge[end_edge_ID]
            end_pos_meter = end_edge_object.get_length()

        if "car_length" in car:
            car_length = car["car_length"]
        else:
            car_length = self.car_default_config["car_length"]

        if "car_type" in car:
            car_type = car["car_type"]
        else:
            car_type = self.car_default_config["car_type"]

        if "route_preference" in car:           
            route_preference = car["route_preference"]
        else:
            route_preference = self.car_default_config["route_preference"]

        if "max_tick_potential" in car:
            max_tick_potential = car["max_tick_potential"]           
        else:
            max_tick_potential = 1

        # calculate path if absent, using "route_preference" as the assignment metric
        if "path" in car:
            path = car["path"]           
        else:    
            potential_paths_list = self.all_paths_depth_first_search(car["start_edge"], car["end_edge"], [], [])
            path = self.choose_path(potential_paths_list, route_preference)


        # create the Car object
        new_car = Car(car["id"],
                        car_length,
                        car["start_edge"],
                        start_pos_meter,
                        car["end_edge"],
                        end_pos_meter,
                        path,
                        car_type,
                        route_preference,
                        max_tick_potential)
        self.car_ID_to_car[new_car.get_car_ID()] = new_car
        start_edge_ID = new_car.get_start_edge()
        start_edge = self.edge_ID_to_edge[start_edge_ID]
        start_edge.add_car_to_wait_queue(new_car)
        print("Adding Car" , new_car.get_car_ID(), "to the Network waiting queue.")


    def check_valid_car(self, car):
        '''Returns a detailed Exception if the given car does not conform to expected input structure.
        '''
        car_ID = car["id"]  # check uniqueness
        if car_ID in list(self.car_ID_to_car.keys()):
            raise Exception("That car ID already exists.")
        
        start_edge_ID = car["start_edge"]
        if start_edge_ID not in list(self.edge_ID_to_edge.keys()):
            raise Exception("Start edge does not exist")

        # Default start_pos_meter set to 0 on addition if absent
        # start_pos_meter = car["start_pos_meter"]
        # start_edge = self.edge_ID_to_edge[start_edge_ID]
        # if start_pos_meter > start_edge.get_length():
        #     raise Exception("Start position exceeds max edge length")

        end_edge_ID = car["end_edge"]
        end_edge = self.edge_ID_to_edge[end_edge_ID]
        end_pos_meter = car["end_pos_meter"]
        if end_pos_meter > end_edge.get_length():
            raise Exception("End position exceeds max edge length")

        # ONLY check path validity if present and unchanging.  Else calculated during "add_car".
        if "path" in car:  
            if car["car_type"] == "Static":
                path_edge_list = car["path"]
                if path_edge_list[-1] != end_edge_ID:
                    raise Exception("Path invalid: end does not match ")
                for edge in path_edge_list:
                    if edge not in list(self.edge_ID_to_edge.keys()):
                        raise Exception("Path has edges that do not exist")
            else:
                print("Calculating path on placement.")
        return True
        

    def remove_node(self, node):
        '''Placeholder for future software version:
        Will remove a Node and all of its associated inbound/outbound Edges from the Network.
        '''
        # raise exception: not implemented yet
        pass

    def remove_edge(self, edge):
        '''Placeholder for future software version:
        Will remove an Edge and all of its associated Cars from the Network.
        '''
        # raise exception: not implemented yet
        pass

    def get_node_from_id(self, node_id):
        '''Uses Network.node_ID_to_node dictionary to map a Node IDs to its corresponding Node object.
        '''
        return self.node_ID_to_node[node_id]

    def get_edge_id(self, edge_id):
        '''Uses Network.edge_ID_to_edge dictionary to map an Edge ID to its corresponding Edge object.
        '''
        return self.edge_ID_to_edge[edge_id]

    def tick(self):
        '''Shuffles the order in which Node ticks will be processed with each global tick to ensure no node is favored.
        Note:  global tick != Node tick.  Global tick is the unit of time until the next state of the simulation, 
        while Node tick the proportion of that time that its components can move uninterrupted.  
        Node ticks will occur until the sum of their durations reaches that of a global tick/no further movement is possible.
        '''
        node_keys = list(self.node_ID_to_node.keys())
        expended_energy = 0                       # work actually done
        sum_maximum_expendible_energy = 0         # maximum work possible

        random.shuffle(node_keys)
        for node_key in node_keys:
            node = self.node_ID_to_node[node_key]
            node_tick_outputs = node.tick()
            expended_energy += node_tick_outputs[0]
            sum_maximum_expendible_energy += node_tick_outputs[1]

        return expended_energy, sum_maximum_expendible_energy

    def restore_tick_potential(self):
        '''Resets the tick_potential to its maximum value for all Cars on the Network.
        '''
        for car_ID in list(self.car_ID_to_car.keys()):
            car_object = self.car_ID_to_car[car_ID]
            new_tick_potential = car_object.get_max_tick_potential() 
            car_object.set_current_tick_potential(new_tick_potential)
            

    def all_paths_depth_first_search(self, current_edge_ID, end_edge_ID, visited_list = [], valid_paths = []):
        '''Given a start and end Edge id, return a list of all valid paths that do not repeat Edges.
        '''
        visited_list.append(current_edge_ID)
        
        current_edge_object = self.edge_ID_to_edge[current_edge_ID]
        edge_terminal_node = current_edge_object.get_end_node()  # returns node object
        neighbouring_edge_IDs_list = list(edge_terminal_node.get_node_outbound())

        for edge_ID in neighbouring_edge_IDs_list:
            current_path = copy.deepcopy(visited_list)

            if edge_ID == end_edge_ID:  # destination edge reached
                current_path.append(edge_ID)
                valid_paths.append(current_path)

            elif not edge_ID in visited_list:
                self.all_paths_depth_first_search(edge_ID, end_edge_ID, current_path, valid_paths)

        # print("Path calculator, current edge ID:", current_edge_ID)        
        # print("Valid_paths so far: ", valid_paths)
        return valid_paths


    def path_cost_distance(self, path_list):
        '''Given path_list, evaluate the total distance it would take to travel.
        This function assumes that the entirety of each Edge is traveled.
        '''
        distance_cost = 0

        for edge_ID in path_list:
            edge_object = self.edge_ID_to_edge[edge_ID]
            distance_cost += edge_object.get_length()
        
        return distance_cost

     
    def path_cost_minimum_time(self, path_list):
        '''Given path_list, evaluate the the minimum time it would take to travel (in ticks) given each Edge's max_speed.
        Minimum time is calculated assuming a car is able to travel the maximum speed per edge unencumbered.
        This function assumes that the entirety of each Edge is traveled and includes any Node-crossing time penalties.
        Note:  time cost does NOT include Node-crossing time out of the final edge as the Car is expected to exit the Network before the Edge's end.
        '''
        time_cost = 0
        final_edge_ID = path_list[-1]

        for edge_ID in path_list:
            edge_object = self.edge_ID_to_edge[edge_ID]
            edge_length = edge_object.get_length()
            edge_speed = edge_object.get_max_speed()
            edge_traversal_time_in_ticks = edge_length/edge_speed
            time_cost += edge_traversal_time_in_ticks

            if edge_ID != final_edge_ID:
                # calculate node crossing time out
                terminal_node = edge_object.get_end_node()
                crossing_cost = terminal_node.get_intersection_time_cost()
                time_cost += crossing_cost

        return time_cost       


    def choose_path(self, all_paths_list, metric):
        '''Given a list of paths from A to B (ex: as calculated using self.all_paths_depth_first_search()),
        returns the "best" path with regards to input metric.
        Currently supported input metrics:
            'Fastest': best path = minimum total travel time (assuming no congestion).
            'Shortest': best path = shortest total distance in terms of length.
            'Random':  pay no heed to metics, choose an available path at random.
        Future versions may include metrics like:
            'Fastest_now': best path = minimum travel time after accounting for current Network congestion.
        '''
        path_cost_list = []

        if metric == 'Fastest':
            for path in all_paths_list:
                path_cost = self.path_cost_minimum_time(path)
                path_cost_list.append(path_cost)
            index_minimum = path_cost_list.index(min(path_cost_list))
            return all_paths_list[index_minimum]
        
        elif metric == 'Shortest':
            for path in all_paths_list:
                path_cost = self.path_cost_distance(path)
                path_cost_list.append(path_cost)
            index_minimum = path_cost_list.index(min(path_cost_list))
            return all_paths_list[index_minimum]

        elif metric == 'Random':
            return random.choice(all_paths_list)

        else:
            raise Exception('"', metric, '" is not a supported metric.  Instead try "Fastest", "Shortest", or "Random".')


class Node:
    def __init__(self, 
                 Network_reference, 
                 id, 
                 intersection_cost, 
                 stoplight_pattern,
                 stoplight_duration,
                 stoplight_delay) -> None:
        '''Contains all functions and attributes pertaining to a network intersection (Node).
        Attributes:
            id:  Unique ID associated with this Node object.
            inbound_edge_ID_to_edge:  Dictionary mapping inbound Edge IDs to Edge objects.
            outbound_edge_ID_to_edge:  Dictionary mapping outbound Edge IDs to Edge objects.
            intersection_time_cost:  Value representing time in ticks required to cross intersection.  0 <= value < 1.
            stoplight_pattern:  Ordered list of sets of simeltaneous Edges eligible for car exiting. Pattern cycles through sets. (Will be implemented in future versions of the software).
            stoplight_pattern_current_index:  Index representing which set of stoplight_pattern the Node is currently on.  (Will be implemented in future versions of the software).
            stoplight_duration: Number of ticks that the stoplight_pattern stays on its current Edge set. (Will be implemented in future versions of the software).
            stoplight_delay: Number of ticks between change of stoplight_pattern Edge sets. (Will be implemented in future versions of the software).
            node_tick_number:  Used in stoplight changes, increments by one with each global TrafficManager tick. (Reference function will be established in future versions of this software).
        '''
        self.id = id
        self.inbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.outbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.intersection_time_cost = intersection_cost    

        self.Network_pointer = Network_reference     # allows Node to call on Network's path-finding algorithms

        self.stoplight_pattern = stoplight_pattern
        self.stoplight_pattern_current_index = 0
        self.stoplight_duration = stoplight_duration
        self.stoplight_delay = stoplight_delay
        self.node_tick_number = self.Network_pointer.get_Network_pointer()


    def add_to_inbound(self, edge):
        '''Used when adding an Edge to the Network when Edge.end_node == self.id .
        Adds the Edge ID and a mapping to its corresponding Edge object to the inbound_edge_ID_to_edge dictionary.
        '''
        self.inbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def add_to_outbound(self, edge):
        '''Used when adding an Edge to the Network when Edge.start_node == self.id .
        Adds the Edge ID and a mapping to its corresponding Edge object to the outbound_edge_ID_to_edge dictionary.
        '''
        self.outbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def get_snapshot(self):
        '''Outputs dictionary of Node attributes.
        '''
        raw = copy.deepcopy(self.__dict__)
        raw.pop("Network_pointer", {})  # exclude from snapshot

        outbound_processing = raw.pop("outbound_edge_ID_to_edge", {})
        raw["outbound_edges"] = list(outbound_processing.keys())
        inbound_processing = raw.pop("inbound_edge_ID_to_edge", {})
        raw["inbound_edges"] = list(inbound_processing.keys())

        return raw      #{"id": self.id}


    def tick(self):
        '''Facilitates Edge ticks and movement of Car objects from one Edge to another.
        If a Car that is eligible to cross the Node has type "Dynamic", then its path is recalculated upon crossing.
        Each Node tick shuffles the order in which Edges tick to ensure no particular Edge is favored. 
        '''
        # print("Current Node Tick: ", self.id)
        expended_energy = 0                       # work actually done
        sum_maximum_expendible_energy = 0         # maximum work possible
        intersection_crossing_cost = self.intersection_time_cost  # absorbs time delay for crossing intersection

        # look for inbound_exit_candidates
        candidate_list_dictionary = self.get_inbound_exit_candidates()
        candidate_cars_list = list(candidate_list_dictionary.values())
        candidate_cars_list.sort(key=lambda x:x.get_current_tick_potential(), reverse=True)  # cars with the highest potential left move first
        
        for car in candidate_cars_list:
            # check if car can be placed on next edge -- allow to exist in intersection (absorbed into intersection cost)
            remaining_potential = car.get_current_tick_potential()
            if remaining_potential >= intersection_crossing_cost:
                if car.get_car_type() == 'Dynamic':   
                    # recalculate path:
                    route_metric = car.get_route_metric()
                    all_possible_paths = self.Network_pointer.all_paths_depth_first_search(car.get_current_edge(), car.get_end_edge(), [], [])
                    new_path = self.Network_pointer.choose_path(all_possible_paths, route_metric)
                    if len(new_path) <= 1:
                        raise Exception("There is no possible path to this car's destination.")
                    new_path = new_path[1:]    # remove current edge
                    car.set_path(new_path)

                # place car on next Edge in path
                car_path = car.get_path()
                next_edge_ID = car_path[0]    
                next_edge_object = self.outbound_edge_ID_to_edge[next_edge_ID]

                # check next edge for capacity
                if len(next_edge_object.get_current_cars()) < next_edge_object.get_max_capacity():
                    # move to position 0 at new edge
                    next_edge_object.move_existing_car_to_edge(car)           
                    car.set_current_edge(next_edge_ID)                        
                    car.set_current_pos_meter_car_front(0) 
                    new_potential = remaining_potential - intersection_crossing_cost  
                    car.set_current_tick_potential(new_potential)
                    car.get_path().pop(0)      # remove current edge from upcoming path
                else:                
                    # place car back on original edge
                    current_edge = car.get_current_edge()
                    current_edge_object = self.inbound_edge_ID_to_edge[current_edge]
                    current_edge_object.move_existing_car_to_edge(car)        # reassociate car and edge with each other

            else:
                # place car back on original edge
                current_edge = car.get_current_edge()
                current_edge_object = self.inbound_edge_ID_to_edge[current_edge]
                current_edge_object.move_existing_car_to_edge(car)        # reassociate car and edge with each other
                
        # advance existing cars on outbound edges as much as possible
        outbound_edge_keys = list(self.outbound_edge_ID_to_edge.keys())
        random.shuffle(outbound_edge_keys)
        for outbound_edge_ID in outbound_edge_keys:
            outbound_edge = self.outbound_edge_ID_to_edge[outbound_edge_ID]
            edge_tick_outputs = outbound_edge.tick()  # move and place new cars, returning list [expended, max] energy
            expended_energy += edge_tick_outputs[0]
            sum_maximum_expendible_energy += edge_tick_outputs[1]

        return expended_energy, sum_maximum_expendible_energy

    def get_inbound_exit_candidates(self):
        '''Checks all inbound edges of a Node.  
        Any edge that has a Car at the end position of its length is considered a candidate to advance on to the next Edge in its path.
        '''
        outbound_candidates = collections.defaultdict(lambda: None)
        for inbound_edge_ID in list(self.inbound_edge_ID_to_edge.keys()):
            inbound_edge = self.inbound_edge_ID_to_edge[inbound_edge_ID]
            inbound_edge_current_cars_list = inbound_edge.get_current_cars()

            # print("N", self.get_node_ID(), " EDGE INBOUND: ", inbound_edge_ID, ":" ,inbound_edge_current_cars_list)
            for car in inbound_edge_current_cars_list:
                current_front_pos = car.get_current_pos_meter_car_front()
                if current_front_pos == inbound_edge.get_length():
                    outbound_candidates[inbound_edge_ID] = car
                    car_index = inbound_edge_current_cars_list.index(car)
                    new_current_cars_list = inbound_edge_current_cars_list[0:car_index] + inbound_edge_current_cars_list[car_index+1::]
                    inbound_edge.set_current_cars(new_current_cars_list)
                    inbound_edge.edge_car_ID_to_car.pop(car.get_car_ID())
                
        # print("N: ", self.id ,"\tcars trying to leave : ", outbound_candidates)
        return outbound_candidates


    def update_stoplight_attributes(self):  
        '''Toggles which Edges allow cars to exit by cycling through sets in stoplight_pattern.
        Returns the set of which inbound Edge set in stoplight_pattern is currently active, or NULL set (denoting red lights for all edges).
        Communication to TrafficManager to establish global tick and increment will be solved in future versions.
        Communication to prevent cars from leaving inbound Edges during the node tick will be established in future versions.
        '''
        open_time = self.stoplight_duration
        off_time_between = self.stoplight_delay
        one_on_off_cycle = open_time + off_time_between

        if self.node_tick_number % one_on_off_cycle in range(open_time + 1, one_on_off_cycle + 1):  # +1 to offset base-0
            # Node is in delay stage, no inbound Edges are open
            return []
        else:
            cycle_index = self.node_tick_number // one_on_off_cycle
            return self.stoplight_pattern[cycle_index]


    def get_node_ID(self):
        '''Returns self.id.
        Used when calling value from outside the Node class.
        '''
        return self.id

    def get_node_inbound(self):
        '''Returns the keys to the dictionary self.inbound_edge_ID_to_edge, list of all inbound Edge IDs.
        Used when calling from outside the Node class.
        '''
        return self.inbound_edge_ID_to_edge.keys()

    def get_node_outbound(self):
        '''Returns the keys to the dictionary self.outbound_edge_ID_to_edge, list of all outbound Edge IDs.
        Used when calling from outside the Node class.
        '''
        return self.outbound_edge_ID_to_edge.keys()

    def get_intersection_time_cost(self):
        '''Returns self.intersection_time_cost, the time penalty it takes to cross a Node.
        Note:  this value may be 0.
        '''
        return self.intersection_time_cost


class Edge:
    def __init__(self,                # TODO:  move value comments to thesis paper
                 id, 
                 start_node_id, 
                 end_node_id, 
                 edge_length,                   # average city block is 80m
                 max_speed,           # default value 0.028 m/s, or about 100 km/h
                 max_capacity           # inf implies no metering/no artificial limit on number of cars allowed on road segment
                 ) -> None:                   # NOTE:  adjust if more fields required
        '''Contains all functions and attributes pertaining to a road segment (Edge).
        Attributes:
            id:  Unique ID associated with this Edge object.
            start_node_id:  Node from which this Edge originates (this Edge is an outbound_edge for start_node).
            end_node_id:  Node from which this Edge terminates (this Edge is an inbound_edge for end_node).
            start_node:  Node object represented by start_node_id.
            end_node:  Node object represented by end_node_id.
            edge_length:  Physical length of the Edge (ex: meter length of a road).
                default value can be found and adjusted at edge_default_config["edge_length"]
            max_speed:  (optional) Unit speed limit of the road.  Without obstructions, this is the maximum distance a Car can move on this Edge in one tick.
                default value can be found and adjusted at edge_default_config["max_speed"]
            max_capacity:  (optional) Maximum number of Car objects allowed on the Edge (max length of current_cars).
                default value can be found and adjusted at edge_default_config["max_capacity"]
            edge_car_ID_to_car:  Dictionary containing all Car objects associated with the Edge; maps Car IDs to Car objects.
            current_cars:  List of IDs of all Cars currently on the Edge.
            waiting_cars:  List of IDs for Cars that are trying to enter the Network at this Edge.
            processed_cars:  List capturing IDs of Cars that have already been processed on the current tick.  Becomes current_cars at the end of the Edge tick.
            completed_cars:  List of IDs of any Cars that have completed their route on this Edge in the duration of the simulation.
        Note:  some attributes have been given default values in the case that the user did not provide them.
        '''
        self.id = id

        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.start_node = self.end_node = None 
        self.edge_length = edge_length

        self.max_speed = max_speed
        self.max_capacity = max_capacity

        self.edge_car_ID_to_car = collections.defaultdict(lambda: None)
        self.current_cars = []
        self.waiting_cars = []
        self.processed_cars = []
        self.completed_cars = []


    def set_start_node(self, node_ptr):
        '''Associates (start) Node pointer with Edge object.
        Used when adding an Edge to the Network.
        '''
        self.start_node = node_ptr

    def set_end_node(self, node_ptr):
        '''Associates (end) Node pointer with Edge object.
        Used when adding an Edge to the Network.
        '''
        self.end_node = node_ptr

    def tick(self):
        '''Facilitates the movement of Car objects traversing this Edge.  There are three types of movement:
            car entry:  a Car from the waiting_car list will be placed on the Edge if and when space becomes available.
            car exiting:  a Car will exit the Network if and when it reaches its end_pos_meter in the process of its movement IF self.id = Car.end_edge.
            car movement:  a Car with status mobile = True will advance as far as possible (maximum potential distance, edge end, or until obstructed by another car).
        '''
        expended_energy = 0                       # work actually done
        sum_maximum_expendible_energy = 0         # maximum work possible

        # Sort Current Cars on starting position, ascending
        self.current_cars.sort(key=lambda x:x.get_current_pos_meter_car_front(), reverse=True)

        # Process any waiting cars
        if len(self.current_cars) < self.max_capacity: 
            for waiting_car in self.waiting_cars:
                car_pos_front = waiting_car.get_start_pos_meter() 
                entry_edge_ID = self.id   
                waiting_car.set_current_edge(entry_edge_ID)
                waiting_car.set_current_pos_meter_car_front(car_pos_front)
                self.processed_cars.append(waiting_car)
                expended_energy += waiting_car.get_max_tick_potential()
                sum_maximum_expendible_energy += waiting_car.get_max_tick_potential()
                waiting_car.set_current_tick_potential(0)     # all energy used entering network
            self.waiting_cars = []
        else:
            print("Edge ", self.id, "has no capacity for waiting cars.  Will try again next tick.")                     

        # Process current cars on edge
        prev_car_back = self.edge_length  # max position a car can travel, resets with each car

        for current_car in self.current_cars:
            current_car_id = current_car.get_car_ID()
            current_car_object = self.edge_car_ID_to_car[current_car_id]
            old_potential = current_car_object.get_current_tick_potential()
            sum_maximum_expendible_energy += old_potential

            if current_car.get_mobility() == False:
                # car is halted and cannot move
                current_car_object.set_current_tick_potential(0)
                self.processed_cars.append(current_car)

            elif current_car.get_current_tick_potential() > 0:  # move only if there is still energy to do so
                current_car_front = current_car_object.get_current_pos_meter_car_front()
                max_distance_full_tick_potential = self.get_max_speed()
                max_distance_current_tick_potential = current_car.get_current_tick_potential() * max_distance_full_tick_potential

                # check if car on destination edge
                if current_car.get_end_edge() == self.id:
                    exit_position = current_car.get_end_pos_meter()
                    dist_to_exit = exit_position - current_car_front

                    if dist_to_exit < min(max_distance_current_tick_potential, prev_car_back - current_car_front):
                        # set positions to destination
                        current_car.set_current_pos_meter_car_front(exit_position)
                        destination_edge_ID = current_car.get_end_edge()
                        current_car.set_current_edge(destination_edge_ID)

                        # car exits -- append to completed_cars and remove from further processing
                        current_car.set_route_status('Route Completed')
                        current_car.set_mobility(False)
                        completed_car_ID = current_car.get_car_ID()
                        self.completed_cars.append(completed_car_ID)
                        self.edge_car_ID_to_car.pop(completed_car_ID)  
                        # del current_car  # car no longer exists
                    else:
                        # otherwise move as far as possible (exit further than travel distance)
                        distance_to_advance = min(max_distance_current_tick_potential, prev_car_back - current_car_front)      # no buffer distance
                        distance_to_advance_ticks = distance_to_advance/self.max_speed   # percent of possible tick moved
                        current_car_object.current_tick_potential -= distance_to_advance_ticks  
                        current_car.current_pos_meter_car_front += distance_to_advance  # actually move
                        expended_energy += current_car.tick(old_potential)   # get potential differential
                        prev_car_back = current_car.current_pos_meter_car_front - current_car.get_car_length()

                        self.processed_cars.append(current_car)
                else:
                    # otherwise move as far as possible
                    distance_to_advance = min(max_distance_current_tick_potential, prev_car_back - current_car_front)      # no buffer distance
                    distance_to_advance_ticks = distance_to_advance/self.max_speed   # percent of possible tick moved
                    current_car_object.current_tick_potential -= distance_to_advance_ticks 
                    current_car.current_pos_meter_car_front += distance_to_advance  # actually move
                    expended_energy += current_car.tick(old_potential)   # get potential differential
                    prev_car_back = current_car.current_pos_meter_car_front - current_car.get_car_length()

                    self.processed_cars.append(current_car)

            else:
                # car has already moved max possible along tick, append to "processed"
                self.processed_cars.append(current_car)

        # edge done processing, set up for next tick
        self.current_cars = self.processed_cars
        self.processed_cars = []
        return expended_energy, sum_maximum_expendible_energy


    def get_snapshot(self):
        '''Outputs dictionary of Edge attributes, including lists of Cars that are:
        currently on the Edge, waiting to enter the Edge, or completed their trip on this Edge.
        '''
        raw = copy.deepcopy(self.__dict__)
        raw.pop("start_node")
        raw.pop("end_node")
        raw.pop("processed_cars")
        raw.pop("edge_car_ID_to_car")

        waiting_cars = raw.pop("waiting_cars", [])
        if waiting_cars != []:
            cleaned_waiting_cars = [car.get_car_ID() for car in waiting_cars]
            raw["waiting_cars"] = cleaned_waiting_cars
        else:
            raw["waiting_cars"] = {}

        current_cars = raw.pop("current_cars", [])    
        if current_cars != []:
            cleaned_current_cars = [car.get_car_ID() for car in current_cars]
            raw["current_cars"] = cleaned_current_cars
        else:
            raw["current_cars"] = {}

        return raw

    def get_edge_ID(self):
        '''Returns self.id.
        Used when calling value from outside the Edge class.
        '''
        return self.id

    def get_start_node(self):
        '''Returns self.start_node Object.
        Used when calling value from outside the Edge class.
        '''
        return self.start_node

    def get_end_node(self):
        '''Returns self.end_node Object.
        Used when calling value from outside the Edge class.
        '''
        return self.end_node

    def get_start_node_id(self):        
        '''Returns self.start_node_id.
        Used when calling value from outside the Edge class.
        '''
        return self.start_node_id
        
    def get_end_node_id(self):       
        '''Returns self.end_node_id.
        Used when calling value from outside the Edge class.
        '''
        return self.end_node_id

    def get_length(self):       
        '''Returns self.edge_length (length of road segment, typically in meters).
        Used when calling value from outside the Edge class.
        '''
        return self.edge_length

    def get_max_speed(self):   
        '''Returns self.max_speed (speed limit of road segment, typically in meters/sec).
        Used when calling value from outside the Edge class.
        '''
        return self.max_speed

    def get_max_capacity(self):       
        '''Returns self.max_capacity.
        Used when calling value from outside the Edge class.
        '''
        return self.max_capacity

    def get_current_cars(self):       
        '''Returns self.current_cars, the list of Car IDs for all cars currently on the Edge.
        Used when calling value from outside the Edge class.
        '''
        return self.current_cars

    def set_current_cars(self, new_list):       
        '''Replaces the list contents of self.current_cars with new_list.
        Used when updating value from outside the Edge class.
        '''
        self.current_cars = new_list

    def add_car_to_wait_queue(self, car):
        '''Adds Car object to the waiting queue and links Car to Edge on Car ID.
        '''
        self.waiting_cars.append(car)
        self.edge_car_ID_to_car[car.get_car_ID()] = car

    def move_existing_car_to_edge(self, car):
        '''Adds Car object to the 'processed-cars' list and links Car to (new) Edge on Car ID.
        '''
        self.processed_cars.append(car)     
        self.edge_car_ID_to_car[car.get_car_ID()] = car

