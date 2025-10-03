# Object oriented implementation of a vector clock


# Data structure for a vector clock
class _Vector_Clock:
    def __init__(self, process_id):
        self.process_id = process_id
        self.vector_clock = {}

    def increment(self, process_id):
        self.vector_clock[process_id] += 1

    def increment_self(self):
        self.increment(self.process_id)

    def set_process_clock(self, value, process_id):
        self.vector_clock[process_id] = value

    def get_clock_dict(self):
        return self.vector_clock
                
# Generates the different vector clocks for each process from the data. Dictionary of (process_id, _Vector_Clock objects)
class Vector_Clock_Generator:
    def __init__(self):
        self.data = {}

        # dictionary of process_id -> unique vector clock
        self.vector_clocks = {}

    # loads the data from a dictionary and generates the vector clocks
    def load_data(self, data):
        # type check
        if not isinstance(data, dict):
            raise ValueError("This method only accepts dictionaries")
        
        self.data = data
        self._intialize_vector_clocks()
        self._generate_vector_clocks()
    

    def _intialize_vector_clocks(self):
        # reset vector clocks
        self.vector_clocks = {}
        for branches, process_ids in self.data.items():
            for process_id in process_ids.keys():
                vc = _Vector_Clock(process_id)
                # simplistic approach, initialize a vector clock for each process with value 0
                for branch_names in self.data.keys():
                    vc.set_process_clock(0, branch_names)
                self.vector_clocks[process_id] = vc
    
    # increments the vector clock for a specific process and branch name
    def increase_vector_clock(self, process_id, branch_name):
        vector_clock = self.vector_clocks[process_id]
        vector_clock.increment(branch_name)

    # sets the vector clock for a specific process and branch name
    def _set_vector_clock(self, process_id, branch_name, value):
        vector_clock = self.vector_clocks[process_id]
        vector_clock.set_process_clock(value, branch_name)
        
    # returns the vector clocks as a dictionary of _Vector_Clock objects
    def get_vector_clocks(self):
        return self.vector_clocks

    # returns the vector clocks as a dictionary of dictionaries  
    def get_vector_clocks_as_dic(self):
        vc_dic = {}
        for process_id, vc in self.vector_clocks.items():
            vc_dic[process_id] = vc.get_clock_dict()
        return vc_dic    
    
    # creates the vector clocks for each process, holds the logic
    def _generate_vector_clocks(self):
         # TODO: implement the logic to generate the vector clocks
         #
         #
         pass