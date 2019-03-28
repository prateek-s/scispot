import json
import tinydb
import os,sys 
import urllib2, os, sys, subprocess
import googleapiclient.discovery
import paramiko
import random
import string 
from jobgen import JobGen

class SciSpot:
    """ Common fields and methods for various SciSpot components """
    
    project='first-220321'
    imageName = 'global/images/ubs5' 
    
    #mtypes_highcpu=['n1-highcpu-64','n1-highcpu-32','n1-highcpu-16','n1-highcpu-8','n1-highcpu-4','n1-highcpu-2']
    mtypes_highcpu=['n1-highcpu-64','n1-highcpu-32','n1-highcpu-16','n1-highcpu-8','n1-highcpu-4']
    mtypes_stan=['n1-standard-1','n1-standard-16','n1-standard-2','n1-standard-32','n1-standard-4','n1-standard-64','n1-standard-8']
    zones=['us-central1-f','us-east1-b','us-east4-c','europe-west4-a','europe-north1-a','asia-southeast1-b']

    compute = googleapiclient.discovery.build('compute', 'v1')

    #User configurable settings 
    zone='us-east1-b'
    username = 'prateek3_14'
    key_filename = '/home/prateeks/.ssh/gce'
    current_master = 'ubslurm1'
    runfile = '/scispot/sb_confinement.sh' 
    param_exporation_file = 'config/nanoconfinement_parameter.json' 
    current_mtype = 'n1-highcpu-4' #Sane default if nothing specified. 

    # load the settings from a config file
    config = {}
    with open('config.json') as json_file:  
        config = json.load(json_file)
        
        zone = config['zone']
        username = config['username']
        key_filename = config['key_filename']
        current_master = config['current_master']
        runfile = config['runfile'] 
        param_exporation_file = config['param_exporation_file']
        current_mtype = config['current_mtype']

    max_params_to_explore = 100
    min_params_to_explore = 80 
    
    ##################################################
    
    def __init__(self):
        #Nothing for now.
        #TODO2: Read above fields from some config file? 
        pass 
    
    def get_jobdb(self):
        """ We use these for ad-hoc locking """
        return tinydb.TinyDB('jobdb.json')

    def get_vmdb(self):
        return tinydb.TinyDB('vmdb.json')

    ##################################################


    def machine_type(self, m):
        #Cat proc/cpuinfo, and some memory ? 
        #cpus = num_cpus()
        cpus = int(m.split('-')[-1])
        machine = {'sockets': 1, 'cores': cpus/2, 'threads': 2, 'cpus':cpus, 'memory': 1000}
        #TODO2: We dont really care about memory for MD jobs. Needs fixing eventually. 
        return machine 

    ##################################################

    def get_instance_ip(self, instance):
        #Let project and zone be global!
        return self.compute.instances().get(project=self.project, zone=self.zone, instance=instance).execute().get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP')


    def gcp_ssh(self, instance):
        instance_ip = self.get_instance_ip(instance)
        #
        client=paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #Copy the new slurm config file 
        client.connect(instance_ip, username=self.username, key_filename=self.key_filename)
        return client

    ##################################################

    def gen_cluster_name(self):
        """ Generate a random name """
        random_name = ''.join([random.choice(string.ascii_lowercase) for n in xrange(6)])
        return random_name

    ##################################################
    
    def select_best_server(self, runtimedict):
        """ Use the running time that we have """
        #TODO: Expected cost based optimization
        #TODO: Insert a cost dictionary and estimated MTTF dict atleast 
        for m in runtimedict.keys():
            r = int(runtimedict[m])
        return 'n1-highcpu-16'
           
    def get_VM_age(self, vmname):
        """ Use api's , current time, etc to return the VM's age in seconds. Use this for calculating probabilities of failure etc """
        pass

    def get_fail_prob(self, mtype, vmnames, T=1):
        """ For a job of length T, what is our fail prob. We use this for...? """ 
        pass

    

    ##################################################
    ##################################################

    
