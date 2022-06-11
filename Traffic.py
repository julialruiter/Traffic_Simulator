import copy
from cmath import inf
import collections
from platform import node

class TrafficManager:
    def __init__(self, network_config) -> None:
        self.graph = Network(network_config)
        pass
    
    def tick(self):
        '''advance state of network'''
        # tick network
        pass

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

    def get_node_neighbours(self):   # todo:  move to node
        pass

    def place_car(self, car):
        pass

    def remove_car(self, car):
        pass

    def advance_car(self, car):
        pass

    def pause_car(self, car):
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


    def get_node_neighbours(self):  
        pass

    def get_snapshot(self):
        '''outputs list of nodes, edges'''
        edge_snapshots = []
        for edge_key in self.edge_ID_to_edge:
            edge = self.edge_ID_to_edge[edge_key]
            edge_raw = edge.get_snapshot()  
            edge_snapshots.append(edge_raw)
        return edge_snapshots
            # TODO:  come back after defining car storage

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
        pass


class Node:
    def __init__(self, id) -> None:
        self.id = id
        self.inbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.outbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.neighbours = collections.defaultdict(lambda: None)  # TODO: calculate later

    def add_to_inbound(self, edge):
        self.inbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def add_to_outbound(self, edge):
        self.outbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def tick(self):
        '''advance state of network on the node level'''
        # tick_edge
        pass

    def change_stoplight(self):   # todoL  deal with later
        '''toggle which edges in and out can move'''
        pass

    def get_node_ID(self):
        '''get object from ID'''
        return self.id


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

        self.id = id
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.edge_length = edge_length
        self.max_speed = max_speed
        self.max_capacity = max_capacity

        self.start_node = self.end_node = None    # Default to None
        self.car_id_to_car = collections.defaultdict(lambda: None)
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
        cars = raw.pop("car_id_to_car", [])
        cars = [i for i in cars.keys()]
        raw.pop("processed_cars")
        
        waiting_cars = raw.pop("waiting_cars", [])
        if waiting_cars != {}:
            cleaned_waiting_cars = [{car.get_car_id() : car.get_snapshot()} for car in waiting_cars]
            raw["waiting_cars"] = cleaned_waiting_cars
        else:
            raw["waiting_cars"] = {}

        current_cars = raw.pop("current_cars", [])    
        if current_cars != []:
            cleaned_current_cars = [{car.get_car_id() : car.get_snapshot()} for car in current_cars]
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

    def get_edge_length(self):
        return self.edge_length

    def get_max_speed(self):
        return self.max_speed

    def get_max_capacity(self):
        return self.max_capacity



class Car:
    def __init__(self) -> None:
        
        pass

    def tick(self):
        '''advance state of network on the car level'''
        pass

    def get_snapshot(self):
        '''outputs car location'''
        return self.__dict__
        pass

    def get_car_ID(self):
        '''get object from ID'''
        return self.id