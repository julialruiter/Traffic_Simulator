import copy
from cmath import inf

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
                if 'static':  Car follows predetermined path.  If no path assigned, a path is generated when the Car is added to the simulation.
                if 'dynamic':  Car will recalculate its route every time it reaches a Node.  (Will be implemented in future versions of the software).
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
        self.mobile = True          # Default.  Toggle to False if API call received OR route complete
        self.route_status = 'In progress'   # Default.  There are also 'Paused' and 'Completed' states.

        self.current_edge = None
        self.current_pos_meter_car_front = None 
        self.max_tick_potential = 1
        self.current_tick_potential = copy.deepcopy(self.max_tick_potential)    # only for initialization


    def tick(self, old_potential):
        '''Calculates "potential" differential;
        This is the portion of a full tick movement completed by the Car on this tick.'''
        return old_potential - self.current_tick_potential

    def get_snapshot(self):
        '''Outputs dictionary of Car attributes.
        '''
        return self.__dict__

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
    def set_path(self, new_path_list):
        self.path = new_path_list

    def get_car_type(self):
        return self.car_type

    def get_mobility(self):
        return self.mobile
    def set_mobility(self, Boolean):
        self.mobile = Boolean

    def get_route_status(self):
        return self.route_status
    def set_route_status(self, new_string):
        self.route_status = new_string

    def get_current_edge(self):
        return self.current_edge
    def set_current_edge(self, edge_ID):
        self.current_edge = edge_ID
    
    def get_current_pos_meter_car_front(self):
        return self.current_pos_meter_car_front
    def set_current_pos_meter_car_front(self, new_position_meters):
        self.current_pos_meter_car_front = new_position_meters

    def get_max_tick_potential(self):
        return self.max_tick_potential

    def get_current_tick_potential(self):
        return self.current_tick_potential     
    def set_current_tick_potential(self, new_potential):
        self.current_tick_potential = new_potential