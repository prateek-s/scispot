import os
import sys
from twisted.web import server, resource, http
from twisted.internet import reactor, endpoints
import json
import logging
import requests
import urlparse
import math
import time
import datetime
import tinydb
import urllib2, os, sys, subprocess
import googleapiclient.discovery
import paramiko
import dateutil
import dateutil.parser
import random
from SciSpot import SciSpot
#from jobgen import JobGen

"""
Usage: http://localhost:7878/?preempted=abacus
http://localhost:7878/?finished=jobid
http://localhost:7878/?launch_cluster=True&namegrp=abra&num_nodes=4&mtype=n1-highcpu-16&start_id=1&slurm_master=ubslurm1

"""


##################################################    ##################################################

class evlisten(resource.Resource, SciSpot):
    """ Main HTTP Server that listens for job launch requests and completion/failure events """

    isLeaf = True  # Required by twisted?

    phases = ['adhoc', 'explore', 'exploit']

    phase = 'adhoc' #Always start out this way

    gen_cc = None #Generator for cluster configs

    cleanup_unused = False #Whether we want to terminate unused VMs or not

    runtimedict = dict() #Store Server type and running time

    current_namegrp = None

    current_cluster = []

    current_mtype = 'n1-highcpu-4' #Sane default if nothing specified. 

    target_nodes = 0 #

    current_jobs = [] #Useful for respawning?

    current_master = 'ubslurm1'

    current_start_id = 1

    ##################################################

    def __init__(self):
        #Open the job and vmdb json databases?
        self.jobs_completed = 0
        self.jobs_abandoned = 0
        #self.compute = googleapiclient.discovery.build('compute', 'v1')

    ##################################################

    def start_master(self, zone, name):
        """ Non-preemptible, with source image, no startup script? """
        mtype = 'n1-standard-2'
        pass

    ##################################################

    def start_worker(self, mtype, zone, name, startupscriptstr):
        """ Hidden inputs: VM-image """

        machine_type = "zones/{}/machineTypes/{}".format(zone, mtype)

        instance_body={
            'name':name,
            'machineType':machine_type,
            'scheduling':
            {
                'preemptible': 'true'
            },
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': self.imageName
                    }
                }],
            'metadata' : {
                "items" : [
                    {
                        "key": "startup-script",
                        "value":startupscriptstr
                    }
                ]
            },
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],
        }
        #print(str(instance_body))

        response = self.compute.instances().insert(project=self.project, zone=self.zone, body=instance_body).execute()
        return response

    ##################################################

    def generate_slurm_config(self, slurm_master, machine, compute_nodes):
        slurmconfstr = """
# slurm.conf file generated by configurator easy.html.
# Put this file on all nodes of your cluster.
# See the slurm.conf man page for more information.
#
ControlMachine={slurm_master}
AuthType=auth/none
#CheckpointType=checkpoint/none
#CryptoType=crypto/munge
#ControlAddr=
#
#MailProg=/bin/mail
MpiDefault=none
#MpiParams=ports=#-#
ProctrackType=proctrack/pgid
ReturnToService=1
SlurmctldPidFile=/var/run/slurm-llnl/slurmctld.pid
#SlurmctldPort=6817
SlurmdPidFile=/var/run/slurm-llnl/slurmd.pid
#SlurmdPort=6818
SlurmdSpoolDir=/var/lib/slurm-llnl/slurmd
#SlurmUser=slurm
SlurmdUser=root
StateSaveLocation=/var/lib/slurm-llnl/slurmctld
SwitchType=switch/none
TaskPlugin=task/none
JobCredentialPrivateKey=/home/prateek3_14/slurmkey
#
JobCompType=jobcomp/filetxt
JobCompLoc=/var/log/slurmjobs
DebugFlags=NO_CONF_HASH
# TIMERS
#KillWait=30
#MinJobAge=300
#SlurmctldTimeout=120
#SlurmdTimeout=300
#
#
# SCHEDULING
FastSchedule=1
SchedulerType=sched/builtin
#SchedulerPort=7321
SelectType=select/linear
#
#
# LOGGING AND ACCOUNTING
AccountingStorageType=accounting_storage/none
ClusterName=ubslurm1
#JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/none
#SlurmctldDebug=3
SlurmctldLogFile=/var/log/slurm-llnl/slurmctld.log
#SlurmdDebug=3
SlurmdLogFile=/var/log/slurm-llnl/slurmd.log
SuspendTime=86400
#
#
# COMPUTE NODES \n""".\
        format(slurm_master=slurm_master)

        slurmconfstr += ' '.join(("NodeName=DEFAULT",
                                  "Sockets="        + str(machine['sockets']),
                                  "CoresPerSocket=" + str(machine['cores']),
                                  "ThreadsPerCore=" + str(machine['threads']),
                                  "State=UNKNOWN"))
        #state=CLOUD otherwise, but doesnt work?

        slurmconfstr += '\n'
        #slurmconfstr += 'NodeName={slurm_master} \n'.format(slurm_master=slurm_master)
        slurmconfstr += 'NodeName={compute_nodes} \n'.format(compute_nodes=compute_nodes)


        slurmconfstr += "\n PartitionName=long Nodes={compute_nodes} Default=YES MaxTime=INFINITE State=UP \n".format(compute_nodes=compute_nodes)
        return slurmconfstr

    ##################################################

    def get_startup_script(self, slurmconfstr):
        """ Copy slurm config, and start slurmd. TODO: if master, then slurmctld"""

        startupscriptstr = """
#!/bin/bash

logger "Startup Script Begins.... "
logger "Running as `whoami`"

systemctl stop slurmd
systemctl stop slurmctld

echo > /etc/slurm-llnl/slurm.conf

cat <<\EOF >> /etc/slurm-llnl/slurm.conf
{slurmconfstr}
EOF

systemctl start slurmd

logger "Slurm conf applied, startup script ending"

exit 0

    """.format(slurmconfstr=slurmconfstr)
        return startupscriptstr

    ##################################################


    def reconfig_master(self, master, slurmconf_str):

        client = self.gcp_ssh(master)

        i, o, e=client.exec_command("cat > /tmp/slurmconf")
        i.write(slurmconf_str)
        i.close()
        client.close()
        #TODO: Can we reuse the same connection?

        client = self.gcp_ssh(master)
        i, o, e=client.exec_command("sudo slurm_reload_cfg /tmp/slurmconf")
        client.close()
        #Above script copies new cfg and restarts slurm daemons
        print("Master reconfigured")
        #TODO: Set up strigger node down for each launched node?
        return


    ##################################################
    ################## Cluster Managment #############

    def launch_cluster(self, namegrp, num_nodes, mtype, start_id=current_start_id, slurm_master=current_master, replenish=False):
        """ Launches worker VMs and reconfigs master if not replenishing """

        machine = self.machine_type(mtype)
        self.current_namegrp = namegrp
        compute_nodes = namegrp + "[1-" + str(num_nodes*3) + "]"
        #*3 is just a margin for safety in case we fail and have to rerun the job without reconfiguring master

        #TODO: Check if requested VMs are available and free, and use them instead of launching? Can get tricky 
        
        configstr = self.generate_slurm_config(slurm_master, machine, compute_nodes)
        cnodes_launched = []
        if slurm_master is None:
            #TODO: Start the master, non-preemptible, and wait
            print("Master must be running, not supported yet, exiting")
            return

        if not replenish :
            #No need to reconfigure the master if we are replacing lost servers
            #TODO: Check this!! Slurmctld may need restarting urghhh
            self.reconfig_master(slurm_master, configstr)

        for i in range(start_id, num_nodes+start_id):
            name = namegrp+str(i)
            self.start_worker(mtype, self.zone, name, self.get_startup_script(configstr))
            cnodes_launched.append(name)
            self.current_cluster.append(name)
            self.current_start_id = i+1
            #Add to the vmdb
            vmdb = self.get_vmdb()
            t_start = datetime.datetime.now().isoformat()
            vmdb.insert({'vmname':name, 't_start':t_start, 'type':mtype, 'status':'running'})
            vmdb.close()
            time.sleep(5)

        self.current_mtype = mtype
        self.target_nodes = num_nodes

        print("Cluster Launched: {}, {}, {}".format(namegrp, mtype, num_nodes))
        return (slurm_master, cnodes_launched)

    ##################################################

    def server_deficit(self):
        target = self.target_nodes
        curr = 0
        instances = self.compute.instances()
        running_vms = [vm.name for vm in instances.list(project=self.project, zone=self.zone, filter="status = RUNNING").execute()['items'] if vm.status is 'RUNNING']
        curr = len(running_vms)
        #TODO: Must be part of this name group (use name), AND must be
        return target - curr

    ##################################################
    
    def replenish_cluster(self):
        """ Launch New VMs to replace the lost ones """ 
        #First, figure out if we need to?
        #return number of nodes launched
        deficit = self.server_deficit()
        if deficit <= 0 :
            print("No replenishment required!")
            return (self.current_namegrp, 0)

        return self.launch_cluster(self.current_namegrp, deficit, self.current_mtype, replenish=True)

    ##################################################

    def destroy_current_cluster(self):
        for c in self.current_cluster:
            #TODO: Google API for stopping and destroy machine
            pass
        self.current_cluster = []

    ##################################################
    #################### Jobs ########################

    def run_job(self, mtype=current_mtype, num_nodes=len(current_cluster), jobparams='', master=current_master):
        """ Run a job on a running with the given jobparams """

        cores = self.machine_type(self.current_mtype)['cores']
        num_nodes = len(self.current_cluster)

        sbatcmd = "sbatch --parsable -N {num_nodes} -c {cores} -n {num_nodes} {runfile} {jobparams}".format(\
            num_nodes=num_nodes, cores=cores, runfile=self.runfile, jobparams=jobparams)
        #Just returns the job-id

        sshclient = self.gcp_ssh(master)
        i, o, e = sshclient.exec_command(sbatcmd)
        jobid = o.read()
        jobid = jobid.strip()
        o.close()
        sshclient.close()

        strigger_fail_cmd = "strigger --set --down --program=/scispot/handle_fail.sh --jobid={}".format(jobid)
        sshclient = self.gcp_ssh(master)
        i, o, e = sshclient.exec_command(strigger_fail_cmd)
        o.close()        
        sshclient.close()

        strigger_fin_cmd = "strigger --set --fini --program /scispot/handle_fin.sh --jobid {}".format(jobid)
        sshclient = self.gcp_ssh(master)
        i, o, e = sshclient.exec_command(strigger_fin_cmd)
        o.close()
        sshclient.close()
        
        
        jobdb = self.get_jobdb()
        t_start = datetime.datetime.now().isoformat()
        jobmetadata = {'jobname':jobid, 't_start':t_start, 'runfile':self.runfile, 'resources':(num_nodes, cores), 'state':'running', 'jobparams':jobparams, 'mtype':mtype, 'num_nodes':num_nodes}
        self.current_jobs.append(jobmetadata)
        jobdb.insert(jobmetadata)
        jobdb.close()
        
        print("Job started {}  {}".format(jobid, sbatcmd))
        
        return jobid

    ##################################################

    def rerun_job(self, jobid=None):
        if jobid is None:
            #pop from the current_jobs
            jobmetadata = self.current_jobs.pop()
            #We assume that the metadata in the DB is consistent?
        else:
            jobdb = self.get_jobdb()
            q = tinydb.Query()
            res = jobdb.search(q.jobname == jobid)
            if len(res) is 0:
                print("Trying to rerun job that doesn't exist!")
                jobdb.close()
                return

            jobmetadata = res[-1]

        jobdb.close()
        jobparams = jobmetadata['jobparams']
        mtype = jobmetadata['mtype']
        num_nodes = jobmetadata['num_nodes']
        
        return self.run_job(jobparams)


    ##################################################
    #################### Exploration #################
    ##################################################

    def cluster_config(self, target_cpus):
        """ Generator for cluster configurations which sum to target_cpus """
        target_cpus = int(target_cpus) 
        for m in self.mtypes_highcpu:
            machine = self.machine_type(m)
            cpus = int(machine['cpus'])
            num_servers = int(math.ceil(target_cpus/cpus))
            #TODO: Need some more checks here?
            if num_servers > 0:
                print((m, num_servers))
                yield (m, num_servers)


    ##################################################
                
    def start_exploration(self, target_cpus):
        """ TODO: Ask for program name! Assumes confinement for now """
        self.target_cpus = target_cpus
        if self.gen_cc is None:
            self.gen_cc = self.cluster_config(self.target_cpus)
        print("Starting the exploration")
        self.phase = 'explore' 
        self.do_exploration()


    ##################################################

    def do_exploration(self):
        """ Called at the start of exploration phase, and after a job finishes """ 
        try:
            (mtype, num_servers) = self.gen_cc.next()
            if self.cleanup_unused:
                self.destroy_current_cluster()

            namegrp = self.gen_cluster_name() #Random string
            self.current_cluster = [] #Reset otherwise run_job tries launching with larger params 
            self.launch_cluster(namegrp, num_servers, mtype)
            jobid = self.run_job()
            #We don't wait, but just return here. Serial exploration. 
        except Exception as e:
            print(e)
            print("Done exploring all?")
            self.selected_mtype = self.select_best_server(self.runtimedict) #Based on E[C] TODO 
            self.current_mtype = self.selected_mtype
            #TODO: Need to either exit cleanly OR continue to exploitation phase somehow
            #TODO: Return the best value that we have seen!
            self.start_exploitation() 
        return


    ##################################################
    #################### Exploitation ################

    def start_exploitation(self):
        self.phase = 'exploit'  #Well thats optimistic!!
        pass
    
    
    def run_next_job(self):
        """ Exploitation phase only. Generate a new set of parameters, and start the job """
        #TODO: Find the next set of parameters, and then call run job
        jobparams = '' 
        #jobparams = jobgen.next()
        self.run_job(jobparams)

    ##################################################
    ################## Event Listeners ###############
    ##################################################


    def handle_finished(self, jobids):
        """ Does a lot more than just handling the event.
        Updates the DB, and decides what to do next depending on the phase """

        if jobids is None or len(jobids) is 0:
            print("empty job string, nothing to do")
            return
        fin_time = datetime.datetime.now().isoformat()
        jobdb = self.get_jobdb()

        for job in jobids:
            #We expect only one job id to finish per strigger, so can remove this loop
            #Will be a string, but that is OK if the keys are strings?
            q = tinydb.Query()
            res = jobdb.search(q.jobname == job)
            if len(res) is 0:
                print("No matching job")
                jobdb.insert({'jobname':job, 't_finish':fin_time})
            else:
                t_start = res[0]['t_start']
                tdiff = (dateutil.parser.parse(fin_time) - dateutil.parser.parse(t_start)).total_seconds()
                jobdb.update({'t_finish':fin_time, 'state':'finished', 'tdiff':tdiff}, q.jobname == job)

        jobdb.close() #For mutual exclusion

        if self.phase is 'explore':
            self.runtimedict[self.current_mtype] = tdiff
            self.jobs_completed += 1
            self.do_exploration() #Try next server configuration, exploration is serial for now!

        elif self.phase is 'exploit':
            self.run_next_job()

        return

    ##################################################


    ##################################################

    def handle_preempted(self, jobids):
        """ We only get the jobid. Find vmids later by scanning compute instances list """
        if jobids is None or len(jobids) is 0:
            print("empty job string, nothing to do")
            return

        fin_time = datetime.datetime.now().isoformat()

        jobdb = self.get_jobdb()

        for job in jobids:
            #Will be a string, but that is OK if the keys are strings?
            q = tinydb.Query()
            res = jobdb.search(q.jobname == job)
            if len(res) is 0:
                print("No matching job for {}".format(job))
                jobdb.insert({'jobname':job, 't_finish':fin_time})
            else:
                jobdb.update({'t_finish':fin_time, 'state':'failed'}, q.jobname == job)

        jobdb.close() #For mutual exclusion

        #TODO: Scan the list of running VMs we have, see which ones are running, find preempted one(s), and find out how many more we need to launch!

        #TODO: We must spawn extra VMs first!!! Find out how many VMs are required?
        self.preemption_reaction(jobids[0])

        return


    def preemption_reaction(self, jobid):
        """Jobid has failed. What do we do? """

        if self.phase is "adhoc":
            print("Adhoc mode, nothing to do on preemption!")
            return 
        
        if self.jobs_completed > self.min_params_to_explore :
            print("Job quota met, nothing remaining!")
            return

        #TODO: Maybe just probabilistically decide based on current success ratio?
        #Not important right now because we randomize the generated jobs
        should_rerun = True
        target_success_rate = float(self.min_params_to_explore)/self.max_params_to_explore
        current_success_rate = float(self.jobs_completed)/max(1.0, float(self.jobs_completed + self.jobs_abandoned))

        # if current_success_rate < target_success_rate:
        #     should_rerun = True
        # r = random.random()

        self.replenish_cluster()

        if should_rerun is True:
            self.rerun_job(jobid)
        else:
            self.jobs_abandoned += 1
            self.run_next_job()


    ##################################################

    def parse_handle_req(self, req_args):
        if 'preempted' in req_args.keys():
            print("preempted")
            #Get the job id
            vals = req_args['preempted']
            self.handle_preempted(vals)

        elif 'finished' in req_args.keys():
            #Get the job id
            print("finished")
            vals = req_args['finished']
            self.handle_finished(vals)

        elif 'launch_cluster' in req_args.keys():
            print(req_args)
            self.launch_cluster(req_args['namegrp'][0], int(req_args['num_nodes'][0]), \
                                req_args['mtype'][0], int(req_args['start_id'][0]), \
                                req_args['slurm_master'][0])

        elif 'run_job' in req_args.keys():
            self.run_job()
            #req_args['master'][0], req_args['num_nodes'][0], req_args['cores'][0])

        elif 'explore' in req_args.keys():
            self.start_exploration(req_args['target_cpus'][0])

        else:
            print("not understood")


        return "OK"

    ##################################################

    def render_GET(self, request):
            #    self.numberRequests += 1
        a = request.args
        print(a)
        to_ret = self.parse_handle_req(a)
        request.setHeader(b"content-type", b"text/plain")
        content = to_ret
        return content.encode("ascii")

##################################################

endpoints.serverFromString(reactor, "tcp:7878").listen(
    server.Site(evlisten()))

reactor.run()
