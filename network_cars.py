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
                 path,
                 car_type,
                 route_preference,
                 max_tick_potential
                 ) -> None:
        '''Contains all functions and attributes pertaining to an object traversing the Network (Car).
        Attributes:
            id:  Unique ID associated with this Car object.
            car_length:  Physical unit length of the Car object (ex: meters).  May be 0.
            start_edge:  Edge from which this Car originates its journey.
            start_pos_meter:  Unit position along start_edge from which the Car begins its journey.  Edge origin = position 0.
            end_edge:  Edge from which this Car terminates its journey.
            end_pos_meter:  Unit position along end_edge at which the Car terminates its journey and leaves the Network.
            path:  Ordered list of Edges that the Car will traverse to get from start to end.
            route_preference:  Classification determining which type of path will be followed:
                if 'Fastest': chooses path with minimum total travel time (assuming no congestion).
                if 'Shortest': chooses path with shortest total distance in terms of length.
                if 'Random':  pays no heed to metics and instead chooses an available path at random.
            car_type:  Car classification for path-following:
                if 'Static':  Car follows predetermined path set on addition.
                if 'Dynamic':  Car will recalculate its route every time it reaches a Node. 
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
            current_tick_potential:  Portion of tick time-distance that the car has not (yet) utilized on this tick.
            '''
        # immutable attributes
        self.id = car_ID
        self.car_length = car_length
        self.start_edge = start_edge
        self.start_pos_meter = start_pos_meter
        self.end_edge = end_edge
        self.end_pos_meter = end_pos_meter

        # attributes pertaining to travel path
        self.car_type = car_type
        self.route_preference = route_preference
        self.path = path

        # addributes pertaining to current status
        self.mobile = True                  # Default.  Toggle to False if API call received OR route complete
        self.route_status = 'In progress'   # Default.  There are also 'Paused' and 'Completed' states.
        self.current_edge = None
        self.current_pos_meter_car_front = None 
        self.max_tick_potential = max_tick_potential
        self.current_tick_potential = copy.deepcopy(self.max_tick_potential)    # only for initialization


    def tick(self, old_potential):
        '''Calculates "potential" differential;
        This is the portion of a full tick movement completed by the Car on this tick.
        '''
        return old_potential - self.current_tick_potential

    def get_snapshot(self):
        '''Outputs dictionary of Car attributes.
        '''
        return self.__dict__

    def get_car_ID(self):
        '''Returns self.id.
        Used when calling value from outside the Car class.
        '''
        return self.id
    
    def get_car_length(self):
        '''Returns self.car_length.
        Used when calling value from outside the Car class.
        '''
        return self.car_length
    
    def get_start_edge(self):
        '''Returns self.start_edge, the Edge at which the Car entered the Network.
        Used when calling value from outside the Car class.
        '''
        return self.start_edge
    
    def get_start_pos_meter(self):
        '''Returns self.start_pos_meter, the position on the start Edge at which the Car entered the Network.
        Used when calling value from outside the Car class.
        '''
        return self.start_pos_meter
    
    def get_end_edge(self):        
        '''Returns self.end_edge, the Edge at which the Car finishes its route and leaves the Network.
        Used when calling value from outside the Car class.
        '''
        return self.end_edge
    
    def get_end_pos_meter(self):      
        '''Returns self.end_pos_meter, the position on the Edge at which the Car finishes its route and leaves the Network.
        Used when calling value from outside the Car class.
        '''
        return self.end_pos_meter

    def get_path(self):
        '''Returns self.path, the ordered list of upcoming Edges the Car will traverse.
        Used when calling value from outside the Car class.
        '''
        return self.path

    def set_path(self, new_path_list):
        '''Replaces self.path with new_path_list, 
        typically removing the first entry as the car enters a new Edge, or when calculating a new route.
        Used when updating value from outside the Car class.
        '''
        self.path = new_path_list

    def get_car_type(self):
        '''Returns self.car_type.
        Value is "Static" (Car remains on its original path) or "Dynamic" (Car recalculates path at every Node crossing).
        Used when calling value from outside the Car class.
        '''
        return self.car_type

    def get_mobility(self):
        '''Returns self.mobile.
        Value is True (Car is eligible to move) or False (Car is halted or its path is complete).
        Used when calling value from outside the Car class.
        '''
        return self.mobile

    def set_mobility(self, Boolean):
        '''Updates the Boolean value of self.mobile to input Boolean.
        Value is True (Car is eligible to move) or False (Car is halted or its path is complete).
        Used when updating value from outside the Car class.
        '''
        self.mobile = Boolean

    def get_route_status(self):
        '''Returns self.route_status.
        Value is "In progress", "Route Completed", "Paused", or "Removed from simulation at tick #n".
        Used when calling value from outside the Car class.
        '''
        return self.route_status
    
    def get_route_metric(self):
        '''Returns self.route_preference.  Used when a Car's path needs to be (re)calculated.
        Value is "Shortest", "Fastest", "Random", with "Random" being the default value if none specified.
        Used when calling value from outside the Car class.
        '''
        return self.route_preference

    def set_route_status(self, new_string):
        '''Updates self.route_status to new_string.
        Value should be "In progress", "Route Completed", "Paused", or "Removed from simulation at tick #n".
        Used when updating value from outside the Car class.
        '''
        self.route_status = new_string

    def get_current_edge(self):        
        '''Returns self.car_length.
        Used when calling value from outside the Car class.
        '''
        return self.current_edge

    def set_current_edge(self, edge_ID):
        '''Replaces self.current_edge with edge_ID.
        Used when updating value from outside the Car class.
        '''
        self.current_edge = edge_ID
    
    def get_current_pos_meter_car_front(self):        
        '''Returns self.current_pos_meter_car_front.
        Used when calling value from outside the Car class.
        '''
        return self.current_pos_meter_car_front

    def set_current_pos_meter_car_front(self, new_position_meters):
        '''Replaces self.current_pos_meter_car_front with new_position_meters.
        Used when updating value from outside the Car class.
        '''
        self.current_pos_meter_car_front = new_position_meters

    def get_max_tick_potential(self):
        '''Returns self.max_tick_potential.
        Used when calling value from outside the Car class.
        '''
        return self.max_tick_potential

    def get_current_tick_potential(self):        
        '''Returns self.current_tick_potential.
        Used when calling value from outside the Car class.
        '''
        return self.current_tick_potential     

    def set_current_tick_potential(self, new_potential):
        '''Replaces self.current_tick_potential with new_potential.
        Used when updating value from outside the Car class.
        '''
        self.current_tick_potential = new_potential


