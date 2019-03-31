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
import shlex 
from SciSpot import SciSpot
from jobgen import JobGen


"""
http://localhost:7878/?explore=True&target_cpus=16
http://localhost:7878/?exploit=True&num_jobs=10
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

    current_master = SciSpot.current_master 
    
    current_mtype = SciSpot.current_mtype

    target_nodes = 0 #

    current_jobs = [] #Useful for respawning?

    current_start_id = 1
    
    current_job_params = ''
    
    jobs_to_run = 0 #Number of jobs in the bag
    jobs_completed = 0
    jobs_abandoned = 0
    jobs_preempted = 0
    completion_rate = 0.9 #What fraction of jobs we want finished

    #global job start time
    jobs_start_time =0

    #global parellel run
    parallel_runs=8
    servers_per_parallel_run=1
    
    
    ##################################################

    def __init__(self):
        #Open the job and vmdb json databases?
        #self.compute = googleapiclient.discovery.build('compute', 'v1')
        pass
    
    ##################################################

    def start_master(self, zone, name):
        """ Non-preemptible, with source image, no startup script? """
        #Usually we start the master manually since it is very long running 
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
            # Removed the accessConfigs so that public IP will not be assigned.
            #'networkInterfaces': [{
            #    'network': 'global/networks/default',
            #    'accessConfigs': [
            #        {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            #    ]
            'networkInterfaces': [{
                'network': 'global/networks/default'
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
JobCredentialPrivateKey=/scispot/slurmkey
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
ClusterName={cluster_name}
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
        format(slurm_master=slurm_master, cluster_name=slurm_master)

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
        master = self.current_master
        startupscriptstr = """
#!/bin/bash

logger "Startup Script Begins.... "
logger "Running as `whoami`"

systemctl stop slurmd
systemctl stop slurmctld

sed -i 's/@ubslurm1/{master}/' /scispot/slurmkey.pub 

echo > /etc/slurm-llnl/slurm.conf

cat <<\EOF >> /etc/slurm-llnl/slurm.conf
{slurmconfstr}
EOF

systemctl start slurmd

logger "Slurm conf applied, startup script ending"

exit 0

    """.format(master=master, slurmconfstr=slurmconfstr)
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
        
        if slurm_master is None:
            if self.current_master is not None:
                slurm_master = self.current_master
            else:
                #TODO: Start the master, non-preemptible, and wait
                print("Master must be running, not supported yet, exiting")
                return
            
        machine = self.machine_type(mtype)
        self.current_namegrp = namegrp

        if not replenish :
            compute_nodes = namegrp + "[1-" + str((self.current_start_id+num_nodes)*3) + "]"
            configstr = self.generate_slurm_config(slurm_master, machine, compute_nodes)
            self.current_configstr = configstr
            self.target_nodes = num_nodes
            #No need to reconfigure the master if we are replacing lost servers
            #TODO: Check this!! Slurmctld may need restarting urghhh
            self.reconfig_master(slurm_master, configstr)
            time.sleep(5)         

        else:
            configstr = self.current_configstr 

        #*3 is just a margin for safety in case we fail and have to rerun the job without reconfiguring master

        #TODO: Check if requested VMs are available and free, and use them instead of launching? Can get tricky 
        

        cnodes_launched = []

        num_nodes_to_lanch = self.target_nodes - len(self.current_cluster)
        #when new nodes are less than the current running nodes this loop will not run
        for i in range(self.current_start_id, num_nodes_to_lanch+self.current_start_id):
            name = namegrp+str(i)
            self.start_worker(mtype, self.zone, name, self.get_startup_script(configstr))
            cnodes_launched.append(name)
            self.current_cluster.append(name)
            self.current_start_id = i+1
            #Add to the vmdb
            vmdb = self.get_vmdb()
            t_start = datetime.datetime.now().isoformat()
            vmdb.insert({'vmname':name, 't_start':t_start, 'type':self.current_mtype, 'status':'running'})
            vmdb.close()
            time.sleep(5)

        if(num_nodes_to_lanch>0):
            print("Cluster Launched: {}, {}, {}, waiting...".format(namegrp, mtype, num_nodes_to_lanch))
            # waiting 90 seconds to let VM launch and ready
            time.sleep(90)
        else:
            print("New insances did not launch, jobs will run using existing VMs")

        print("Current start id is {}".format(self.current_start_id))

        return (slurm_master, cnodes_launched)

    ##################################################

    def get_all_VMS_by_NGroup(self, name_group):
        try:
            nameGroupREX = name_group + '*'
            instances = self.compute.instances()
            # added an extra filter to get current instances which are in same machine type
            lauched_vms = [vm['name'].encode("ascii") for vm in instances.list(project=self.project, zone=self.zone, filter="(name = " + nameGroupREX + ")").execute()['items'] if vm['machineType'].encode("ascii").split("/")[-1] == self.current_mtype]
            #running_vms = [vm['name'].encode("ascii") for vm in instances.list(project=self.project, zone=self.zone, filter="status = RUNNING").execute()['items']]
            return lauched_vms
        except Exception as e:
            print("Error getting Launched VMs!")
            print(e)
            return []

    def get_running_VMS(self):
        try:
            instances = self.compute.instances()
            # added an extra filter to get current instances which are in same machine type
            running_vms = [vm['name'].encode("ascii") for vm in instances.list(project=self.project, zone=self.zone, filter="(status = RUNNING)").execute()['items'] if vm['machineType'].encode("ascii").split("/")[-1] == self.current_mtype]
            #running_vms = [vm['name'].encode("ascii") for vm in instances.list(project=self.project, zone=self.zone, filter="status = RUNNING").execute()['items']]
            return running_vms
        except Exception as e:
            print("Error getting running VMs!")
            print(e)
            return []
        
    def server_deficit(self):
        target = self.target_nodes
        curr = 0
        try:
            running_vms = self.get_running_VMS()
        except:
            print("Launching Nothing")
            return 0
        
        namegrp_vms = [vmname for vmname in running_vms if self.current_namegrp in vmname]
        print("VM's currently running {}".format(namegrp_vms))
        
        curr = len(namegrp_vms)
        
        #set current cluster to the running VM names
        self.current_cluster = namegrp_vms
        
        #TODO: Must be part of this name group (use name), AND cannot be the master 
        return target - curr

    ##################################################
    
    def replenish_cluster(self):
        """ Launch New VMs to replace the lost ones """ 
        #First, figure out if we need to?
        #return number of nodes launched
        deficit = self.server_deficit()
        print("Server deficit: {}".format(deficit))
        if deficit <= 0 :
            print("No replenishment required!")
            return (self.current_namegrp, 0)

        print("Replenishing {} VMs with IDs starting from {}".format(deficit, self.current_start_id))
        
        return self.launch_cluster(self.current_namegrp, deficit, self.current_mtype, replenish=True)

    ##################################################

    def destroy_current_cluster(self):
        for c in self.current_cluster:
            #TODO: Google API for stopping and destroy machine
            pass
        self.current_cluster = []

    ##################################################
    #################### Jobs ########################

    def run_job(self, mtype=current_mtype, num_nodes=None, jobparams='', master=current_master):
        """ Run a job on a running with the given jobparams """

        cores = self.machine_type(self.current_mtype)['cores']

        if num_nodes is None:
            num_nodes = len(self.current_cluster)


        sbatcmd = "sbatch --no-requeue --parsable -N {num_nodes} -c {cores} -n {num_nodes} {runfile} {jobparams}".format(\
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
        jobmetadata = {'jobname':jobid, 't_start':t_start, 'runfile':self.runfile, 'resources':(num_nodes, cores), 'state':'running', 'jobparams':jobparams, 'mtype':self.current_mtype, 'num_nodes':num_nodes}
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
            if jobmetadata['state'] == 'rerun':
                print("Job already marked as rerun")
                return
            
            jobdb.update({'state':'rerun'}, q.jobname == jobid)

        jobdb.close()
        
        jobparams = jobmetadata['jobparams']
        mtype = jobmetadata['mtype']
        num_nodes = jobmetadata['num_nodes']

        if self.phase is "exploit":
            self.run_job(num_nodes=self.servers_per_parallel_run, jobparams=jobparams)
        else:
            self.run_job(jobparams=jobparams)

        return 


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
        self.jobs_start_time = datetime.datetime.now().isoformat()
        self.phase = 'explore' 
        self.do_exploration()


    ##################################################

    def check_if_cluster_ready(self):
        is_cluster_not_ready=True
        #SSH into the master
        #Issue sinfo -h, and then get number of nodes
        #replenish_cluster()
        #If not, then wait 90 seconds more.
        while is_cluster_not_ready :
            #This gets how many nodes are up
            #sinfo -h | awk '{if (($5=="alloc") || ($5=="idle")) sum += $4} END {print sum}'
            nodes_cmd = "sinfo -h | awk '{if (($5==\"alloc\") || ($5==\"idle\")) sum += $4} END {print sum}'"
            #Just returns the number of nodes available
            sshclient = self.gcp_ssh(self.current_master)
            i, o, e = sshclient.exec_command(nodes_cmd)
            nodes_num = o.read()
            nodes_num = nodes_num.strip()
            o.close()
            sshclient.close()

            if nodes_num == None or nodes_num is '':
                nodes_num = '0'

            print("Number of nodes required = "+str(self.target_nodes)+" ,nodes running = "+ nodes_num)

            if self.target_nodes <= int(nodes_num):
                is_cluster_not_ready=False
            else:
                #We want to give slurm some time to reconfigure...
                self.replenish_cluster()
                # waiting time moved to launch cluster.
                #time.sleep(90)

        return

    def manage_VM_group(self):
        # This function makesure the reutilization of the currenly running VMs
        namegrp = None
        running_vms = self.get_running_VMS()
 
        print("VM's currently running {}, which are the type of {}".format(running_vms, self.current_mtype))
            
        if running_vms :
            namegrp = running_vms[-1][0:6]
            self.current_namegrp = namegrp
            namegrp_vms = [vmname for vmname in running_vms if self.current_namegrp in vmname]
            #This is to get the next available index for a VM group
            all_vms = self.get_all_VMS_by_NGroup(namegrp)
            # sort the VM names by the last few digits
            all_vms.sort(key = lambda x: int(x[6:]))
            print("All the VM's previously launched {}, for the namegroup = {}".format(all_vms, self.current_namegrp))
            self.current_start_id = int(all_vms[-1][6:])+1
            self.current_cluster = namegrp_vms 

        else:
            print("There is no running VMS for machine_type = "+ self.current_mtype)
            print("Selecting a new cluster name group")
            namegrp = self.gen_cluster_name() #Random string
            self.current_namegrp = namegrp
            self.current_cluster = [] #Reset otherwise run_job tries launching with larger params
            self.current_start_id = 1

        return


    def do_exploration(self):
        """ Called at the start of exploration phase, and after a job finishes """ 
        try:
            (mtype, num_servers) = self.gen_cc.next()
            self.current_mtype = mtype
            if self.cleanup_unused:
                self.destroy_current_cluster()

            #Check whether same type VMS are up and running; if so use them combine this with self.cleanup_unused later
            self.manage_VM_group()

            self.launch_cluster(self.current_namegrp, num_servers, self.current_mtype)

            #make sure cluster is ready
            self.check_if_cluster_ready()

            #if cluster is ready run the job
            jobid = self.run_job() 
            #We don't wait, but just return here. Serial exploration. 
        except Exception as e:
            print(e)
            print("Done exploring all?")
            self.selected_mtype = self.select_best_server(self.runtimedict) #Based on E[C] TODO 
            self.current_mtype = self.selected_mtype
            
            #TODO: Need to either exit cleanly OR continue to exploitation phase somehow
            #TODO: Return the best value that we have seen!
            #self.start_exploitation(1)
            #Too optimiistic
        return


    ##################################################
    #################### Exploitation ################

    def start_exploitation(self, num_jobs, mtype=current_mtype, num_servers=servers_per_parallel_run, parallel_runs=parallel_runs ,completion_rate=0.9):
        self.phase = 'exploit'  #Well thats optimistic!!
        self.completion_rate = completion_rate
        self.current_mtype = mtype
        pd = {}

        with open(self.param_exporation_file) as json_file:  
            pd = json.load(json_file)

        num_jobs = int(num_jobs)
        jg = JobGen(pd, num_jobs)

        min_jobs = jg.num_fixed_params()
        self.job_gen = jg.gen_job_param()

        jobs_to_run = max(min_jobs, num_jobs)
        self.jobs_to_run = jobs_to_run

        print("Kickstarting bag of jobs of size {}".format(jobs_to_run))
        
        #Check whether same type VMS are up and running; if so use them
        self.manage_VM_group()

        self.launch_cluster(self.current_namegrp, num_servers*parallel_runs, self.current_mtype)
        
        #We want to give slurm some time to reconfigure...
        #make sure cluster is ready
        self.check_if_cluster_ready()

        self.jobs_start_time = datetime.datetime.now().isoformat()

        #Parellel job runs
        for x in range(parallel_runs):
            jobparams = self.job_gen.next()
            jobid = self.run_job(num_nodes=num_servers, jobparams=jobparams)
            time.sleep(5)

    ##################################################
    ##################################################

    def continue_exploitation(self):
        """ Returns true if we need to keep running jobs in the bag, else false """
        if self.phase != 'exploit':
            return True 
        if self.jobs_completed > self.completion_rate*self.jobs_to_run :
            return False 
        return True

    ##################################################
    
    def run_next_job(self):
        """ Exploitation phase only. Generate a new set of parameters, and start the job """
        #TODO: Find the next set of parameters, and then call run job
        jobparams = ''
        if self.phase is 'exploit':
            if not self.continue_exploitation():
                print("No more jobs to run!")
                return 
            jobparams = self.job_gen.next()
            print("Running next job {}".format(jobparams))
        
        #make sure cluster is ready
        self.check_if_cluster_ready()

        return self.run_job(num_nodes=self.servers_per_parallel_run, jobparams=jobparams)

    ##################################################
    ################## Event Listeners ###############
    ##################################################


    def verify_job_completion(self, jobid):
        """ Return true IFF job actually finished successfully """
        completed = False

        #SSH and Copy the file tail -n 1 /var/log/slurmjobs
        #What if we rerun something and the job 
    
        client = self.gcp_ssh(self.current_master)

        varifyCMD =  "cat /var/log/slurmjobs | awk '/JobId="+str(jobid).strip()+"/ && /JobState=COMPLETED/ {print}'"

        i, o, e=client.exec_command(varifyCMD)
        s = o.read()
        o.close()
        client.close()
        print(s)
        #Check if
        #s="JobId=151 UserId=kadupitiya(1003) GroupId=kadupitiya(1004) Name=sb_confinement.sh JobState=COMPLETED Partition=long TimeLimit=UNLIMITED StartTime=2019-03-26T17:42:01 EndTime=2019-03-26T18:19:55 NodeList=acoiis[1-8] NodeCnt=0 ProcCnt=16 WorkDir=/home/kadupitiya ReservationName= Gres= Account= QOS= WcKey= Cluster=unknown SubmitTime=2019-03-26T17:42:01 EligibleTime=2019-03-26T17:42:01 DerivedExitCode=0:0 ExitCode=0:0
        try:
            d = dict(token.split('=') for token in shlex.split(s))
            print("Found job id " + d['JobId'])
            print("Job id search target " + jobid) 
            if d['JobId'].strip() == jobid.strip():
                print(d['JobState'])
                if d['JobState'].strip() == 'COMPLETED' :
                    completed = True
                    return completed
        except:
            return completed 
        
        return completed 


    ##################################################
    
    def handle_finished(self, jobids):
        """ Does a lot more than just handling the event.
        Updates the DB, and decides what to do next depending on the phase """

        if jobids is None or len(jobids) is 0:
            print("empty job string, nothing to do")
            return

        if not self.verify_job_completion(jobids[0]):
            #There is a race condition if both preemption and finished call backs are called.
            #We fix this by checking the slurmjobs log to see if it /really/ completed
            print("False alarm on the job completion, ignoring!")
            return
        
        fin_time = datetime.datetime.now().isoformat()
        print("Job {} finished at {}".format(jobids[0], fin_time))
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
                print("Job running time (seconds) : {}".format(tdiff))
                
                jobdb.update({'t_finish':fin_time, 'state':'finished', 'tdiff':tdiff}, q.jobname == job)

        jobdb.close() #For mutual exclusion

        self.jobs_completed += 1

        #Time since the start of this job runs
        tdiff_total = (dateutil.parser.parse(fin_time) - dateutil.parser.parse(self.jobs_start_time)).total_seconds()
        print("Total time spend running these jobs since begining (seconds) : {}".format(tdiff_total))
        print("Total jobs completed : {}".format(self.jobs_completed))
        print("Total jobs preempted : {}".format(self.jobs_preempted))
        print("Total jobs abandoned : {}".format(self.jobs_abandoned))

        if self.phase is 'explore':
            self.runtimedict[self.current_mtype] = tdiff
            #TODO: Persist this runtime dict as another json db, pickle, or log 
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
            #Will be a hopefully santized string
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

    ##################################################

    def preemption_reaction(self, jobid):
        """Jobid has failed. What do we do? """

        if self.phase is "adhoc":
            print("Adhoc mode, nothing to do on preemption!")
            return 
        
        if self.phase is "exploit" and not self.continue_exploitation():
            print("Job quota met, nothing remaining!")
            print("We have met our job target! {} {}".format(self.jobs_completed, self.jobs_to_run))
            return

        #TODO: Maybe just probabilistically decide based on current success ratio?
        #Not important right now because we randomize the generated jobs
        #target_success_rate = float(self.min_params_to_explore)/self.max_params_to_explore
        #current_success_rate = float(self.jobs_completed)/max(1.0, float(self.jobs_completed + self.jobs_abandoned))
        # if current_success_rate < target_success_rate:
        #     should_rerun = True
        # r = random.random()
        
        should_rerun = True
            
        if should_rerun is True:
            #Also mark job for re-running?
            self.replenish_cluster()
            #make sure cluster is ready
            self.check_if_cluster_ready()

            self.rerun_job(jobid)
            self.jobs_preempted += 1
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

        elif 'exploit' in req_args.keys():
            self.start_exploitation(req_args['num_jobs'][0])

            
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
