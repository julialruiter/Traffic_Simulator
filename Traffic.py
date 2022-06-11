

class TrafficManager:
    def __init__(self) -> None:
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
    def __init__(self) -> None:
        pass

    def get_node_neighbours(self):  
        pass

    def get_snapshot(self):
        '''outputs list of nodes, edges'''
        pass

    def add_node(self, node):
        pass

    def add_edge(self, edge):
        pass

    def remove_node(self, node):
        # raise exception: not implemented yet
        pass

    def remove_edge(self, edge):
        # raise exception: not implemented yet
        pass

    def get_node(self, node):
        '''get object from ID'''
        pass

    def get_edge(self, node):
        '''get object from ID'''
        pass

    def tick(self):
        # tick_node
        pass


class Node:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network on the node level'''
        # tick_edge
        pass

    def change_stoplight(self):   # todoL  deal with later
        '''toggle which edges in and out can move'''
        pass

    def get_node_ID(self):
        '''get object from ID'''
        pass


class Edge:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network on the edge level'''
        # tick_car
        pass

    def get_edge_ID(self):
        '''get object from ID'''
        pass


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
        pass