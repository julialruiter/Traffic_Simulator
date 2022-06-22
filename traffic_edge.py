import collections
import copy
from cmath import inf

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
        # self.end_node_ID_to_node = collections.defaultdict(lambda: None)    # for neighbours    

        self.max_speed = max_speed
        self.max_capacity = max_capacity

        self.edge_car_ID_to_car = collections.defaultdict(lambda: None)
        self.current_cars = []
        self.waiting_cars = []
        self.processed_cars = []
        self.completed_cars = []


    def set_start_node(self, node_ptr):
        '''Associates (start) Node pointer with Edge object.
        '''
        self.start_node = node_ptr

    def set_end_node(self, node_ptr):
        '''Associates (end) Node pointer with Edge object.
        '''
        self.end_node = node_ptr

    def tick(self):
        '''advance state of network on the edge level'''
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

    def get_current_cars(self):
        return self.current_cars
    def set_current_cars(self, new_list):
        self.current_cars = new_list

    def add_car_to_wait_queue(self, car):
        '''Adds Car object to the waiting queue and links Car to Edge on Car ID.'''
        self.waiting_cars.append(car)
        self.edge_car_ID_to_car[car.get_car_ID()] = car
    def move_existing_car_to_edge(self, car):
        '''Adds Car object to the 'processed-cars' list and links Car to (new) Edge on Car ID.'''
        self.processed_cars.append(car)     # CURRENT cars:  putting on processed cars artifically increases congestion metric
        self.edge_car_ID_to_car[car.get_car_ID()] = car
