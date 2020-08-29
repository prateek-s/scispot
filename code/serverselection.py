import os, sys, math
import urllib2
from SciSpot import Scispot

class ServerSelection(SciSpot):
    
    def __init__(self):
        pass

    def start_exploration(self, target_cores):
        """ Given a target number of cores, find the best server type """
        # Need to start somewhere. Heuristics here?
        for m in self.mtypes_highcpu:
            machine = self.machine_type(m)
            cpus = machine['cpus']
            num_servers = math.ceil(target_cores/cpus)
            #run job (job, m, num_servers)
            runtime = self.run_job(master, num_servers, cores=machine['cores'])
            #Cant do these in parallel because need a separate slurm master for each.
            #So, serial it is!

            
    def best_server(self):
        """ First, we need for expts to finish """ 
        pass

    
