This is a (semi-generalized) Traffic Simulator software.  Though originally designed to handle road/car traffic, "Car" properties have been assigned in such as way that the model may easily be adapted and used for other types of Networks (server traffic, shipping logistics, etc).
Suggested uses, adaptations, and general design motivations have been detailed in the corresponding Thesis Paper repository here:  https://github.com/julialruiter/NetworkTrafficSimulation_Thesis_Paper

This is an open-source project, so any suggestions/contributions for adding features and expanding use cases are appreciated.

Please refer to the page links in the Traffic_Simulator wiki for documentation for each module.

Using the Traffic_Simulator:

1) Create the file you will use to initiate the simulation and import the TrafficManager module (will be available on pip later).  Look at the example "main.py" for an example on how to run a simulation, output snapshots, and add/remove/pause cars in the middle of the simulation.

2) Create the Network/road structure you want the simulation to run on.  This can be manually configured (see "EXAMPLE_network_config.json" for reference), or you may import the UnderlyingNetworkGenerator module and run one of the functions to methodically generate a Network.  UnderlyingNetworkGenerator  currently supports complete bidirectional networks and basic Erdos-Renyi networks.  Future versions of this module will include the option to assign other attributes probabilistically.

3)  Create the Car objects that will traverse the Network.  These may be manually configured (see "EXAMPLE_car_config.json" for reference), or may be systematically generated via an external generator module.  Future versions of Traffic_Simulator will have an embedded generator.

4)  Check the DEFAULT configs files.  If attributes are missing from the user-specified Network input (or Car input), they will be filled in with the default values from these files, and typically assigns any non-essential values to 'None' while assigning a fixed constant for essential values.  You may also want to consider using the DEFAULT config files as a basis for generation if you are creating many similar objects of one type.

