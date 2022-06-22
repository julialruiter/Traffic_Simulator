from traffic_node import Node
from traffic_edge import Edge
from traffic_car import Car
import collections
import random

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
        new_node = Node(node["node_ID"])
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
        '''Shuffles the order in which Nodes will be processed with each tick to ensure no node is favored.
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