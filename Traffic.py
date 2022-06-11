

class TrafficManager:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network'''
        # tick_node
        # tick_edge
        # tick_car
        pass

    def get_snapshot(self):
        '''outputs list of nodes, edges, car locations'''
        pass

    def get_node_neighbours(self):   # todo:  move to node
        pass

    def place_car(self, car):
        pass

    def remove_car(self, car):
        pass

    def advance_car(self, car):
        pass


class Network:
    def __init__(self) -> None:
        pass


class Node:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network on the node level'''
        # tick_edge
        # tick_car
        pass

class Edge:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network on the edge level'''
        # tick_car
        pass

class Car:
    def __init__(self) -> None:
        pass

    def tick(self):
        '''advance state of network on the car level'''
        pass