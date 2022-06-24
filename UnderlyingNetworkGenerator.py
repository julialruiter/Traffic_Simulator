import collections
from cmath import inf

class NetworkGenerator:
    def __init__(self) -> None:
        '''Class containing various functions for generation Network objects for the simulation to run on.
        Th Network can also be provided via custom JSON file instead.
        '''
        self.info = "Please see individual generator functions for more info."


    def output_Network_dictionary(self):
        '''Returns dictionary containing all Node and Edge information for the newly generated Network.
        '''
        pass


    def generate_basic_complete_bidirectional_network(self, number_nodes):
        '''Generates a complete Network consisting of number_nodes Nodes, each connected to every other Node in both directions.
        This Network uses default values for many Node and Edge fields:
            node.intersection_time_cost = 0
            edge.edge_length = 5
            edge.max_speed = 1
            edge.max_capacity = 100
        '''
        number_nodes = number_nodes
        # create Node objects
        complete_network_node_ID_to_node = collections.defaultdict(lambda: None)
        complete_network_edge_ID_to_edge = collections.defaultdict(lambda: None)

        for node_index in range(0,number_nodes):
            node_ID = node_index
            new_node = Node(node_ID)
            complete_network_node_ID_to_node[node_ID] = new_node
            
        # create Edge objects -- requires Nodes to exist first
        edge_index_counter = 0
        edge_length = 5
        max_speed = 1
        max_capacity = 100

        for start_node in range(0,number_nodes):
            for end_node in range(0,number_nodes):
                if start_node == end_node:
                    pass  # no looping roads allowed
                else:
                    # ensure uniquw Edge IDs
                    inbound_edge_ID = edge_index_counter
                    edge_index_counter += 1
                    new_inbound_edge = Edge(inbound_edge_ID, start_node, end_node, edge_length, max_speed, max_capacity)
                    complete_network_edge_ID_to_edge[inbound_edge_ID] = new_inbound_edge

                    outbound_edge_ID = edge_index_counter
                    edge_index_counter += 1
                    new_outbound_edge = Edge(outbound_edge_ID, end_node, start_node, edge_length, max_speed, max_capacity)
                    complete_network_edge_ID_to_edge[outbound_edge_ID] = new_outbound_edge
        
        return complete_network_node_ID_to_node, complete_network_edge_ID_to_edge


class Node:
    def __init__(self, id) -> None:
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
        self.intersection_time_cost = 0 


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
            '''
        self.id = id
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.start_node = self.end_node = None 
        self.edge_length = edge_length
        self.max_speed = max_speed
        self.max_capacity = max_capacity
