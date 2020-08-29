import os,sys

class Server:
    state = 'running' #Or 'preempted'

class Job:
    Job_states = ['todo', 'running', 'preempt-discarded', 'preempt-resumed', 'completed'] 
    state = 'todo'


class JobGroup:
    num_jobs = 10
    done = 0
    
class Cluster:
    #maps servers to job groups and all that 



    def server_preempted(s):
        s.state="preempted" 
        J = get_running_job(s)
        
        if J is None:
            print("No job was running, Ignoring the preemption")
            return

        n = get_BoJ_progress(J) #Just the job-number/Total-num-jobs really.
    
    
        
