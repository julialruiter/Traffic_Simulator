import collections
import copy
from cmath import inf

class Node:
    def __init__(self, id) -> None:
        '''Contains all functions and attributes pertaining to a network intersection (Node).
        Attributes:
            id:  Unique ID associated with this Node object.
            inbound_edge_ID_to_edge:  Dictionary mapping inbound Edge IDs to Edge objects.
            outbound_edge_ID_to_edge:  Dictionary mapping outbound Edge IDs to Edge objects.
            intersection_time_cost:  Value representing time-distance required to cross intersection.
        '''
        self.id = id
        self.inbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        self.outbound_edge_ID_to_edge = collections.defaultdict(lambda: None)
        # self.neighbours = collections.defaultdict(lambda: None)  # TODO: calculate later
        self.intersection_time_cost = 0    # weight representing time (ex: time it takes to transverse intersection)

    def add_to_inbound(self, edge):
        self.inbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def add_to_outbound(self, edge):
        self.outbound_edge_ID_to_edge[edge.get_edge_ID()] = edge

    def get_snapshot(self):
        '''Outputs dictionary of Node attributes.
        Current version only returns ID; future versions will include stoplight information.
        '''
        raw = copy.deepcopy(self.__dict__)
        return {"id": self.id}
        #  TODO:  use the deepcopy when implmenting inbound and outbound


    def tick(self):
        '''Facilitates Edge ticks and movement of Car objects from one Edge to another.
        Each Node tick '''
        print("Current Node Tick: ", self.id)
        expended_energy = 0                       # work actually done
        sum_maximum_expendible_energy = 0         # maximum work possible
        intersection_crossing_cost = self.intersection_time_cost  # absorbs time delay for crossing intersection

        # look for inbound_exit_candidates
        candidate_list_dictionary = self.get_inbound_exit_candidates()
        candidate_cars_list = list(candidate_list_dictionary.values())
        candidate_cars_list.sort(key=lambda x:x.get_current_tick_potential(), reverse=True)  # cars with the highest potential left move first
        for car in candidate_cars_list:
            remaining_potential = car.get_current_tick_potential()
            # check if car can be placed on next edge -- allow to exist in intersection (absorbed into intersection cost)
            if remaining_potential >= intersection_crossing_cost:
                car_path = car.get_path()
                next_edge_ID = car_path[0]      
                # print("Node Outbound Dict:", self.outbound_edge_ID_to_edge)
                # print(next_edge_ID)
                next_edge_object = self.outbound_edge_ID_to_edge[next_edge_ID]
                # print(self.outbound_edge_ID_to_edge)
                # print(next_edge_object)

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
        for outbound_edge_ID in list(self.outbound_edge_ID_to_edge.keys()):
            outbound_edge = self.outbound_edge_ID_to_edge[outbound_edge_ID]
            edge_tick_outputs = outbound_edge.tick()  # move and place new cars, returning list [expended, max] energy
            expended_energy += edge_tick_outputs[0]
            sum_maximum_expendible_energy += edge_tick_outputs[1]
        return expended_energy, sum_maximum_expendible_energy

    def get_inbound_exit_candidates(self):
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
        return self.id

    def get_node_inbound(self):
        return self.inbound_edge_ID_to_edge.keys()

    def get_node_outbound(self):
        return self.outbound_edge_ID_to_edge.keys()
