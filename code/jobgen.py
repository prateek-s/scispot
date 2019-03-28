import os,sys
import json
import numpy as np
import itertools
import random

##################################################

class JobGen:

    """ ParamDict = list of param

param={'type':<types>, 'values':<values>}
    
<types> = 'range' | 'set'

<values> = [min, max] | [v1, v2, ... vn]
"""
    param_sweep_list = []
    param_list = []
    ed = dict()
    d = dict()
    
    def __init__(self, param_dict, max_jobs):
        self.d = param_dict #TODO: JSON read 
        self.max_jobs = max_jobs
        self.output = []
        #self.expanded = dict() #Expand ranges to NP arrays
        #self.num_params = dict() #Number to sample from each 
        #self.n = self.min_params()  #Min value

    def num_fixed_params(self):
        """ Total combinations with fixed params only """ 
        fixed_params = 1 
        for p in self.d:
            v = self.d.get(p) #"p":{"type":"set", "values":[1,2,3,4]}
            if v["type"] == "set":
                num_values = len(v["values"])
                fixed_params *= num_values 
        return fixed_params

    def expand_dict(self):
        """ Based on the min number of parameters, create an expanded dictionary with np arrays """
        n = self.num_fixed_params()
        N = self.max_jobs
        #Each array gets N/n points
        ed = dict()
        for p in self.d:
            v = self.d.get(p) #"p":{"type":"set", "values":[1,2,3,4]}
            if v["type"] == "set":
                ed[p] = v['values']
            elif v["type"] == "range":
                val_range = v["values"]
                assert(len(val_range) >= 2)
                new_vals = np.linspace(val_range[0], val_range[-1], N/n)
                #newv = {'type':'range', 'values':new_vals}
                ed[p] = new_vals

        self.ed = ed
        return ed 

    def gen_combinations(self):
        """ Use the expanded dictionary to generate unique combinations """
        params = self.ed.keys()
        self.param_list = params
        ip = itertools.product(*(self.ed[n] for n in params))
        self.generated_combos = list(ip)
        random.shuffle(self.generated_combos)
        return self.generated_combos 

    def gen_string_for_combo(self, param_tuple):
        """ For a given combination, generate an output string """
        s = ""
        for i,p in enumerate(self.param_list):
            val = param_tuple[i]
            s += '-{} {} '.format(p, val)

        return s

    def gen_job_param(self):
        """ This is the primary entry point """ 
        self.num_fixed_params()
        self.expand_dict()
        self.gen_combinations()

        for c in self.generated_combos:
            yield self.gen_string_for_combo(c)


'''
##################################################

# testd = {'b':{'type':'set', 'values':[1,2,3]}, 'c':{'type':'range', 'values':[1,10]}}
pd = { 
    'Z' : {'type':'range', 'values':[3.0, 4.0]},
    'p' : {'type':'set', 'values': [1, 2, 3]},
    'n' : {'type':'set', 'values':[-1]},
    'd' : {'type':'set', 'values': [0.714]},
    'c' : {'type':'range', 'values':[0.3, 0.9]},
}

jg = JobGen(pd, 100)


print(jg.gen_job_param().next())
print(jg.gen_job_param().next())
print(jg.gen_job_param().next())

print(jg.num_fixed_params())
# print(jg.expand_dict())
# print(jg.gen_combinations())
# print(jg.gen_string(jg.generated_combos[0]))
      
#combinations = it.product(*(my_dict[Name] for Name in allNames))
'''