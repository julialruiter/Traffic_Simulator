from asyncio.windows_events import NULL
import collections

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
        pass

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
            self.add_node(node["node_ID"])

    def get_node_neighbours(self):  
        pass

    def get_snapshot(self):
        '''outputs list of nodes, edges'''
        pass

    def add_node(self, node_id):
        new_node = Node(node_id)
        self.node_ID_to_node[node_id] = new_node

    def add_edge(self, edge):
        pass

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
    def __init__(self, id) -> None:
        self.id = id
        self.start_node_ID_to_node = collections.defaultdict(lambda: None)   # not actually needed 
        self.end_node_ID_to_node = collections.defaultdict(lambda: None)    # for neighbours

    def tick(self):
        '''advance state of network on the edge level'''
        # tick_car
        pass

    def get_edge_ID(self):
        '''get object from ID'''
        return self.id


class Car:
    def __init__(self) -> None:
        
        pass

    def tick(self):
        '''advance state of network on the car level'''
        pass

    def get_snapshot(self):
        '''outputs car location'''
        pass

    def get_car_ID(self):
        '''get object from ID'''
        return self.id