import os,sys
import json
import numpy as np

class JobGen(class):

    param_sweep_list = []
    
    def __init__(self, param_dict, N):
        self.d = param_dict
        self.N = N
        self.output = []
        self.expanded = dict() #Expand ranges to NP arrays
        self.num_params = dict() #Number to sample from each 
        self.n = self.min_params()  #Min value

    def min_params(self):
        fixed_params = 1 
        for param in d.keys():
            v = d.get(param)
            if isinstance(v, list):
                #For explicit values
                self.num_params[param] = len(v)
                fixed_params = fixed_params*len(v)
        return fixed_params
        
    def get_joblist(self, N):
        """ Return a list of jobs of at most N size """
        #Can we assert : N > product(len(v)) for all v
        fixed_params = 1 
        for param in d.keys():
            v = d.get(param)
            if isinstance(v, list):
                #For explicit values
                self.num_params[param] = len(v)
                fixed_params = fixed_params*len(v)


                
            
            elif isinstance(v, tuple):
                #For range
                np.linspace(v[0], v[1], n)
            
