import collections
import copy
import random
from cmath import inf

class Network:
    def __init__(self, config) -> None:
        '''Contains all functions and attributes pertaining to the (road) network as a whole.
        Attributes:
            node_ID_to_node:  Dictionary mapping Node IDs to Node objects.
            edge_ID_to_edge:  Dictionary mapping Edge IDs to Edge objects.
            car_ID_to_car:  Dictionary mapping Car IDs to Car objects.

        '''
        self.node_ID_to_node = collections.defaultdict(lambda: None)
        self.edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.car_ID_to_car = collections.defaultdict(lambda: None)

        for node in config["node_list"]:
            self.add_node(node)
        for edge in config["edge_list"]:
            self.add_edge(edge)

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
        new_node = Node(node["node_ID"], self)  # adds Network reference
        if self.node_ID_to_node[new_node.get_node_ID()]:
            raise Exception("There is already a Node with this ID")
        self.node_ID_to_node[new_node.get_node_ID()] = new_node

    def add_edge(self, edge):
        '''Imports edge(s) from given edge dictionary.
        If both the start and end nodes are already in the network, then the edge will be added.
        '''
        new_edge = Edge(edge["edge_ID"],
                        edge["start_node"],
                        edge["end_node"],
                        edge["edge_length"],
                        edge["max_speed"],
                        edge["max_capacity"] )
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
        '''Places car (object) on the waiting queue for its specified start_edge.
        '''
        new_car = Car(car["car_ID"],
                        car["car_length"],
                        car["start_edge"],
                        car["start_pos_meter"],
                        car["end_edge"],
                        car["end_pos_meter"],
                        car["path"],
                        car["car_type"] )
        # print("We are adding" , new_car.get_car_ID(), new_car)
        self.car_ID_to_car[new_car.get_car_ID()] = new_car
        start_edge_ID = new_car.get_start_edge()
        start_edge = self.edge_ID_to_edge[start_edge_ID]
        start_edge.add_car_to_wait_queue(new_car)


    def check_valid_car(self, car):
        '''Returns a detailed Exception if the given car does not conform to expected input structure.
        '''
        car_ID = car["car_ID"]  # check uniqueness
        if car_ID in list(self.car_ID_to_car.keys()):
            raise Exception("That car ID already exists.")
        
        start_edge_ID = car["start_edge"]
        if start_edge_ID not in list(self.edge_ID_to_edge.keys()):
            raise Exception("Start edge does not exist")

        start_pos_meter = car["start_pos_meter"]
        start_edge = self.edge_ID_to_edge[start_edge_ID]
        if start_pos_meter > start_edge.get_length():
            raise Exception("Start position exceeds max edge length")

        end_edge_ID = car["end_edge"]
        end_edge = self.edge_ID_to_edge[end_edge_ID]
        end_pos_meter = car["end_pos_meter"]
        if end_pos_meter > end_edge.get_length():
            raise Exception("End position exceeds max edge length")

        if car["car_type"] == "static":
            path_edge_list = car["path"]
            if path_edge_list[-1] != end_edge_ID:
                raise Exception("Path invalid: end does not match ")
            for edge in path_edge_list:
                if edge not in list(self.edge_ID_to_edge.keys()):
                    raise Exception("Path has edges that do not exist")
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
        '''Given path_list, evaluate the the minimum time it would take to travel (in ticks).
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
        '''Given a list of paths from A to B (ex: as calculated using self.all_paths_depth_first_search),
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
    def __init__(self, id, Network_reference) -> None:
        '''Contains all functions and attributes pertaining to a network intersection (Node).
        Attributes:
            id:  Unique ID associated with this Node object.
            inbound_edge_ID_to_edge:  Dictionary mapping inbound Edge IDs to Edge objects.
            outbound_edge_ID_to_edge:  Dictionary mapping outbound Edge IDs to Edge objects.
            intersection_time_cost:  Value representing time in ticks required to cross intersection.  0 <= value < 1.
        '''
        self.id = id
        self.inbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.outbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.intersection_time_cost = 0    # weight representing time (ex: time it takes to transverse intersection)
        self.Network_pointer = Network_reference

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
        network_pointer = raw.pop("Network_pointer", {})

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
        print("Current Node Tick: ", self.id)
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
                if car.get_car_type() == 'Dynamic':   # TODO:  fix reference to Network Class from Nodes Function
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


    def change_stoplight(self):  
        '''Toggles which edges allow cars to exit.
        Will be created in future versions.
        '''
        pass

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
    def __init__(self, 
                 id, 
                 start_node_id, 
                 end_node_id, 
                 edge_length, 
                 max_speed = 0.028,           # default value 0.028 m/s, or about 100 km/h
                 max_capacity = inf           # inf implies no metering/no artificial limit on number of cars allowed on road segment
                 ) -> None:                   # NOTE:  adjust if more fields required
        '''Contains all functions and attributes pertaining to a road segment (Edge).
        Attributes:
            id:  Unique ID associated with this Edge object.
            start_node_id:  Node from which this Edge originates (this Edge is an outbound_edge for start_node).
            end_node_id:  Node from which this Edge terminates (this Edge is an inbound_edge for end_node).
            start_node:  Node object represented by start_node_id.
            end_node:  Node object represented by end_node_id.
            edge_length:  Physical length of the Edge (ex: meter length of a road).
            max_speed:  (optional) Unit speed limit of the road.  Without obstructions, this is the maximum distance a Car can move on this Edge in one tick.
            max_capacity:  (optional) Maximum number of Car objects allowed on the Edge (max length of current_cars).
            edge_car_ID_to_car:  Dictionary containing all Car objects associated with the Edge; maps Car IDs to Car objects.
            current_cars:  List of IDs of all Cars currently on the Edge.
            waiting_cars:  List of IDs for Cars that are trying to enter the Network at this Edge.
            processed_cars:  List capturing IDs of Cars that have already been processed on the current tick.  Becomes current_cars at the end of the Edge tick.
            completed_cars:  List of IDs of any Cars that have completed their route on this Edge in the duration of the simulation.
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
                    current_car_object.current_tick_potential -= distance_to_advance_ticks  # TODO:  
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
        print("move existing troubleshooting: ", self.id)
        self.processed_cars.append(car)     
        self.edge_car_ID_to_car[car.get_car_ID()] = car


class Car:
    def __init__(self, 
                 car_ID,
                 car_length,
                 start_edge,
                 start_pos_meter,
                 end_edge,
                 end_pos_meter,
                 path = [],
                 car_type = 'Static') -> None:
        '''Contains all functions and attributes pertaining to an object traversing the Network (Car).
        Attributes:
            id:  Unique ID associated with this Car object.
            car_length:  Physical unit length of the Car object (ex: meters).  May be 0.
            start_edge:  Edge from which this Car originates its journey.
            start_pos_meter:  Unit position along start_edge from which the Car begins its journey.  Edge origin = position 0.
            end_edge:  Edge from which this Car terminates its journey.
            end_pos_meter:  Unit position along end_edge at which the Car terminates its journey and leaves the Network.
            path:  Ordered list of Edges that the Car will traverse to get from start to end.
            car_type:  Car classification for path-following:
                if 'Static':  Car follows predetermined path.  If no path assigned, a path is generated when the Car is added to the simulation.
                if 'Dynamic':  Car will recalculate its route every time it reaches a Node.  (Will be implemented in future versions of the software).
            mobile:  Car classification for mobility:
                if True:  Car is eligible to move (default).
                if False:  Car has been halted and will not move until further instructions given.
            route_status:  string explaining the Car's status with regards to path completion:
                'In progress':  The Car is eligible for movement; the Car is moving along its path.
                'Route Completed':  The Car has reached its destination and has been removed from the Network.
                'Paused':  The Car is ineligible for movement due to mobile=False.
                'Removed from simulation at tick #n':  The Car was removed from the simulation by external intervention.  n denotes timestamp at which it was removed.
            current_edge:  Edge ID corresponding to the Car's current location.
            current_pos_meter_car_front:  Unit distance along current_edge corresponding to the Car's current location.  If car_length > 0, this refers to the position of the front of the Car.
            max_tick_potential:  Proportion of global maximum tick time-distance that the Car is eligible to move (default = 1, full potential).
            current_tick_potential:  Portion of tick time-distance that the car has not utilized on this tick.
            '''
        self.id = car_ID
        self.car_length = car_length
        self.start_edge = start_edge
        self.start_pos_meter = start_pos_meter
        self.end_edge = end_edge
        self.end_pos_meter = end_pos_meter
        self.path = path
        self.car_type = car_type
        self.route_preference = 'Random'   # TODO:  set later, make "Random" default value
        self.mobile = True          # Default.  Toggle to False if API call received OR route complete
        self.route_status = 'In progress'   # Default.  There are also 'Paused' and 'Completed' states.

        self.current_edge = None
        self.current_pos_meter_car_front = None 
        self.max_tick_potential = 1
        self.current_tick_potential = copy.deepcopy(self.max_tick_potential)    # only for initialization


    def tick(self, old_potential):
        '''Calculates "potential" differential;
        This is the portion of a full tick movement completed by the Car on this tick.
        '''
        return old_potential - self.current_tick_potential

    def get_snapshot(self):
        '''Outputs dictionary of Car attributes.
        '''
        return self.__dict__

    def get_car_ID(self):
        '''Returns self.id.
        Used when calling value from outside the Car class.
        '''
        return self.id
    
    def get_car_length(self):
        '''Returns self.car_length.
        Used when calling value from outside the Car class.
        '''
        return self.car_length
    
    def get_start_edge(self):
        '''Returns self.start_edge, the Edge at which the Car entered the Network.
        Used when calling value from outside the Car class.
        '''
        return self.start_edge
    
    def get_start_pos_meter(self):
        '''Returns self.start_pos_meter, the position on the start Edge at which the Car entered the Network.
        Used when calling value from outside the Car class.
        '''
        return self.start_pos_meter
    
    def get_end_edge(self):        
        '''Returns self.end_edge, the Edge at which the Car finishes its route and leaves the Network.
        Used when calling value from outside the Car class.
        '''
        return self.end_edge
    
    def get_end_pos_meter(self):      
        '''Returns self.end_pos_meter, the position on the Edge at which the Car finishes its route and leaves the Network.
        Used when calling value from outside the Car class.
        '''
        return self.end_pos_meter

    def get_path(self):
        '''Returns self.path, the ordered list of upcoming Edges the Car will traverse.
        Used when calling value from outside the Car class.
        '''
        return self.path

    def set_path(self, new_path_list):
        '''Replaces self.path with new_path_list, 
        typically removing the first entry as the car enters a new Edge, or when calculating a new route.
        Used when updating value from outside the Car class.
        '''
        self.path = new_path_list

    def get_car_type(self):
        '''Returns self.car_type.
        Value is "Static" (Car remains on its original path) or "Dynamic" (Car recalculates path at every Node crossing).
        Used when calling value from outside the Car class.
        '''
        return self.car_type

    def get_mobility(self):
        '''Returns self.mobile.
        Value is True (Car is eligible to move) or False (Car is halted or its path is complete).
        Used when calling value from outside the Car class.
        '''
        return self.mobile

    def set_mobility(self, Boolean):
        '''Updates the Boolean value of self.mobile to input Boolean.
        Value is True (Car is eligible to move) or False (Car is halted or its path is complete).
        Used when updating value from outside the Car class.
        '''
        self.mobile = Boolean

    def get_route_status(self):
        '''Returns self.route_status.
        Value is "In progress", "Route Completed", "Paused", or "Removed from simulation at tick #n".
        Used when calling value from outside the Car class.
        '''
        return self.route_status
    
    def get_route_metric(self):
        '''Returns self.route_preference.  Used when a Car's path needs to be (re)calculated.
        Value is "Shortest", "Fastest", "Random", with "Random" being the default value if none specified.
        Used when calling value from outside the Car class.
        '''
        return self.route_preference

    def set_route_status(self, new_string):
        '''Updates self.route_status to new_string.
        Value should be "In progress", "Route Completed", "Paused", or "Removed from simulation at tick #n".
        Used when updating value from outside the Car class.
        '''
        self.route_status = new_string

    def get_current_edge(self):        
        '''Returns self.car_length.
        Used when calling value from outside the Car class.
        '''
        return self.current_edge

    def set_current_edge(self, edge_ID):
        '''Replaces self.current_edge with edge_ID.
        Used when updating value from outside the Car class.
        '''
        self.current_edge = edge_ID
    
    def get_current_pos_meter_car_front(self):        
        '''Returns self.current_pos_meter_car_front.
        Used when calling value from outside the Car class.
        '''
        return self.current_pos_meter_car_front

    def set_current_pos_meter_car_front(self, new_position_meters):
        '''Replaces self.current_pos_meter_car_front with new_position_meters.
        Used when updating value from outside the Car class.
        '''
        self.current_pos_meter_car_front = new_position_meters

    def get_max_tick_potential(self):
        '''Returns self.max_tick_potential.
        Used when calling value from outside the Car class.
        '''
        return self.max_tick_potential

    def get_current_tick_potential(self):        
        '''Returns self.current_tick_potential.
        Used when calling value from outside the Car class.
        '''
        return self.current_tick_potential     

    def set_current_tick_potential(self, new_potential):
        '''Replaces self.current_tick_potential with new_potential.
        Used when updating value from outside the Car class.
        '''
        self.current_tick_potential = new_potential

