import copy
from cmath import inf
import collections
import random

class TrafficManager:
    def __init__(self, network_config) -> None:
        self.graph = Network(network_config)
        self.timestamp = 0
        pass
    
    def tick(self):
        '''advance state of network'''
        self.timestamp += 1
        self.graph.tick()


    def get_snapshot(self):
        '''outputs list of nodes, edges, car locations'''
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
        pass  

    def get_timestamp(self):
        return self.timestamp  

    def get_node_edges_in_out(self, node_ID):   # todo:  move to node
        node = self.graph.get_node_from_id(node_ID)
        inbound_edge_list = list(node.get_node_inbound())
        outbound_edge_list = list(node.get_node_outbound())
        node_output = {}
        node_output["node_id"] = node_ID
        node_output["inbound_edges"] = inbound_edge_list
        node_output["outbound_edges"] = outbound_edge_list
        print(node_output)

    def add_car(self, car):
        if self.graph.check_valid_car(car) == True:
            self.graph.add_car(car)

    def remove_car(self, car_id):
        pass

    def resume_car(self, car_id):
        pass

    def pause_car(self, car_id):
        pass


class Network:
    def __init__(self, config) -> None:
        self.node_ID_to_node = collections.defaultdict(lambda: None)
        self.edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.car_ID_to_car = collections.defaultdict(lambda: None)
        for node in config["node_list"]:
            self.add_node(node)
        # print(self.node_ID_to_node)
        for edge in config["edge_list"]:
            self.add_edge(edge)

    def get_snapshot(self):
        '''outputs list of nodes, edges'''
        car_set = set()
        snapshot = {}

        edge_snapshots = []
        for edge_key in self.edge_ID_to_edge:
            edge = self.edge_ID_to_edge[edge_key]
            edge_raw = edge.get_snapshot()
            for car_id in edge_raw["waiting_cars"]:  # TODO:  add method for taking cars from "Current_cars" dict
                car_set.add(car_id)
            edge_snapshots.append(edge_raw)
        snapshot["edges"] = edge_snapshots

        node_snapshots = []
        for node_key in self.node_ID_to_node:
            node = self.node_ID_to_node[node_key]
            node_raw = node.get_snapshot()  
            node_snapshots.append(node_raw)
        snapshot["nodes"] = node_snapshots

        car_snapshots = []
        for car_id in car_set:
            car = self.car_ID_to_car[car_id]
            car_raw = car.get_snapshot()
            car_snapshots.append(car_raw)
        snapshot["cars"] = car_snapshots
        return snapshot

    def add_node(self, node):
        '''imports from node dictionary'''
        new_node = Node(node["node_ID"])
        if self.node_ID_to_node[new_node.get_node_ID()]:
            raise Exception("There is already a Node with this ID")
        self.node_ID_to_node[new_node.get_node_ID()] = new_node

    def add_edge(self, edge):
        '''imports from edge dictionary'''
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
                start_node.add_to_inbound(new_edge)

                end_node = self.node_ID_to_node[new_edge.get_end_node_id()]
                new_edge.set_end_node(end_node)
                end_node.add_to_outbound(new_edge)

                self.edge_ID_to_edge[new_edge.get_edge_ID()] = new_edge
            else:
                raise Exception("End Node ID DNE")
        else:
            raise Exception("Start Node ID DNE")

    def add_car(self, car):
        new_car = Car(car["car_ID"],
                        car["car_length"],
                        car["start_edge"],
                        car["start_pos_meter"],
                        car["end_edge"],
                        car["end_pos_meter"],
                        car["path"],
                        car["car_type"] )
        print("We are adding" , new_car.get_car_ID(), new_car)
        self.car_ID_to_car[new_car.get_car_ID()] = new_car
        start_edge_ID = new_car.get_start_edge()
        start_edge = self.edge_ID_to_edge[start_edge_ID]
        start_edge.add_car_to_wait_queue(new_car)


    def check_valid_car(self, car):
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
        # raise exception: not implemented yet
        pass

    def remove_edge(self, edge):
        # raise exception: not implemented yet
        pass

    def get_node_from_id(self, node_id):
        '''get object from ID'''
        return self.node_ID_to_node[node_id]

    def get_edge_id(self, edge_id):
        '''get object from ID'''
        return self.edge_ID_to_edge[edge_id]

    def tick(self):
        # tick_node
        node_keys = list(self.node_ID_to_node.keys())
        random.shuffle(node_keys)
        for node_key in node_keys:
            node = self.node_ID_to_node[node_key]
            print(node)
            node.tick()

class Node:
    def __init__(self, id) -> None:
        self.id = id
        self.inbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.outbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.neighbours = collections.defaultdict(lambda: None)  # TODO: calculate later
        self.intersection_time_cost = 0    # weight representing time (ex: time it takes to transverse intersection)

    def add_to_inbound(self, edge):
        self.inbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def add_to_outbound(self, edge):
        self.outbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def get_snapshot(self):
        raw = copy.deepcopy(self.__dict__)
        return {"id": self.id}
        #  TODO:  use the deepcopy when implmenting inbound and outbound


    def tick(self):
        '''advance state of network on the node level'''
        outbound_candidates = {}

        for inbound_edge_key in list(self.inbound_edge_ID_to_edge.keys()):
            inbound_edge = self.inbound_edge_ID_to_edge[inbound_edge_key]
            inbound_edge_current_cars_list = inbound_edge.get_current_cars()
            print("INBOUND_EDGE_CAR_LIST:", inbound_edge_current_cars_list)
            max_dist_per_tick = inbound_edge.get_max_speed()
            edge_length = inbound_edge.get_length()

            outbound_candidates_per_edge = []
            for car in inbound_edge_current_cars_list:
                print('cars' ,inbound_edge_current_cars_list)
                current_front_pos = car[1][0]
                print(current_front_pos)
                potential_pos_after_tick = current_front_pos + max_dist_per_tick
                if potential_pos_after_tick > edge_length + self.intersection_time_cost:
                    outbound_candidates_per_edge.append([car, potential_pos_after_tick - self.intersection_time_cost - self.edge_length])
            outbound_candidates[inbound_edge_key] = outbound_candidates_per_edge

        print("ob ", outbound_candidates)



    def change_stoplight(self):   # todoL  deal with later
        '''toggle which edges in and out can move'''
        pass

    def get_node_ID(self):
        return self.id

    def get_node_inbound(self):
        return self.inbound_edge_ID_to_edge.keys()

    def get_node_outbound(self):
        return self.outbound_edge_ID_to_edge.keys()

class Edge:
    def __init__(self, 
                 id, 
                 start_node_id, 
                 end_node_id, 
                 edge_length, 
                 max_speed = 6,  # default value 6 m/s
                 max_capacity = inf
                 ) -> None:  # NOTE:  adjust if more fields required
        # self.start_node_ID_to_node = collections.defaultdict(lambda: None)   # not actually needed 
        # self.end_node_ID_to_node = collections.defaultdict(lambda: None)    # for neighbours
        self.edge_car_ID_to_car = collections.defaultdict(lambda: None)
        self.id = id
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.edge_length = edge_length
        self.max_speed = max_speed
        self.max_capacity = max_capacity

        self.start_node = self.end_node = None    # Default to None
        self.current_cars = []
        self.waiting_cars = []
        self.processed_cars = []

    def set_start_node(self, node_ptr):
        self.start_node = node_ptr

    def set_end_node(self, node_ptr):
        self.end_node = node_ptr

    def tick(self):
        '''advance state of network on the edge level'''

        # Sort Current Cars on starting position, ascending
        self.current_cars.sort(key=lambda x:x[1][0])
        # tick_car
        pass

    def get_snapshot(self):
        raw = copy.deepcopy(self.__dict__)
        raw.pop("start_node")
        raw.pop("end_node")
        raw.pop("processed_cars")
        raw.pop("edge_car_ID_to_car")

        waiting_cars = raw.pop("waiting_cars", [])
        if waiting_cars != []:
            cleaned_waiting_cars = [car[0] for car in waiting_cars]
            raw["waiting_cars"] = cleaned_waiting_cars
        else:
            raw["waiting_cars"] = {}

        current_cars = raw.pop("current_cars", [])    
        if current_cars != []:
            cleaned_current_cars = [car[0] for car in current_cars]
            raw["current_cars"] = cleaned_current_cars
        else:
            raw["current_cars"] = {}

        return raw

    def get_edge_ID(self):
        return self.id

    def get_start_node(self):
        return self.start_node
    def get_end_node(self):
        return self.end_node

    def get_start_node_id(self):
        return self.start_node_id
    def get_end_node_id(self):
        return self.end_node_id

    def get_length(self):
        return self.edge_length

    def get_max_speed(self):
        return self.max_speed

    def get_max_capacity(self):
        return self.max_capacity

    def add_car_to_wait_queue(self, car):
        car_pos_object = [car.get_car_ID(), [car.get_start_pos_meter(), car.get_end_pos_meter()]]
        self.waiting_cars.append(car_pos_object)
        self.edge_car_ID_to_car[car.get_car_ID()] = car

    def get_current_cars(self):
        return self.current_cars

class Car:
    def __init__(self, 
                 car_ID,
                 car_length,
                 start_edge,
                 start_pos_meter,
                 end_edge,
                 end_pos_meter,
                 path,
                 car_type) -> None:

        self.id = car_ID
        self.car_length = car_length
        self.start_edge = start_edge
        self.start_pos_meter = start_pos_meter
        self.end_edge = end_edge
        self.end_pos_meter = end_pos_meter
        self.path = path
        self.car_type = car_type

    def tick(self):
        '''advance state of network on the car level'''
        pass

    def get_snapshot(self):
        '''outputs car location'''
        return self.__dict__
        pass

    def get_car_ID(self):
        return self.id
    
    def get_car_length(self):
        return self.car_length
    
    def get_start_edge(self):
        return self.start_edge
    
    def get_start_pos_meter(self):
        return self.start_pos_meter
    
    def get_end_edge(self):
        return self.end_edge
    
    def get_end_pos_meter(self):
        return self.end_pos_meter

    def get_path(self):
        return self.path

    def get_car_type(self):
        return self.car_type