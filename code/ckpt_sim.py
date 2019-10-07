import os,sys,math
import pprint
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

####!! ACHTUNG. RUN using python3. Python2 gives the wrong results! WHY!?!!?!?!?!

######################################################################
"""
Implements the Dynamic Programming based optimal checkpointing.  All values in minutes. 
"""
class DPCkpt:

    soldict=dict()
    C = 1 #Time it takes to write a checkpoint. 1 Minute
    R = 1 #Recovery time
    MTTF = 12*60 #TODO, this is not super accurate. 
    Num_servers = 1
    job_start_time = 0*60
    dp_table = None 
    
    def __init__(self, job_len = 1, job_start_time = 1, faildist="CDF"):
        self.soldict=dict()
        self.job_start_time = job_start_time 
        self.job_len = job_len #In Minutes 
        self.faildist= "CDF" # "empirical" #"expon" #or empirical
        self.ckpt_schedule = dict()
        
        self.C = 1 #Time it takes to write a checkpoint. 1 Minute
        self.R = 1 #Recovery time
        self.MTTF = 12*60 #TODO, this is not super accurate. 
        self.Num_servers = 1

        #(A, B, tau1, tau2) = (0.41370591, 24,  0.9 ,  0.76)
        self.cdfparam = dict({'A':0.4137 , 'tau1':0.9 , 'tau2':0.76, 'b':24 })
        
        #fails_full=np.array([86460.7, 2363.482, 86439.649, 88954.991, 88949.557, 1245.761, 88928.863, 4810.814, 22303.542, 2392.038, 4648.701, 76766.687, 6563.444, 38889.587, 88462.394, 88456.938, 895.826, 401.218, 86488.147, 86480.014, 86474.189, 86467.604, 86462.225])/60.0

        #gcp_cdf=ECDF(fails_full)

    ######################################################################


    def get_raw_sol_table(self):
        """ Main entry point """ 
        self.dp_table = self.makespan(self.job_len, 0, 0, self.job_start_time, 0)

    ##################################################
        
    def get_Exp_running_time(self):
        try:
            #parse the dp_table somehow.... Needs averaging? 
            pass
        except:
            pass

    ##################################################
    
    def get_checkpoint_schedule(self):
        #use the dp_table for something ?
        maxdict = dict() #Not sure if this is entirely correct. Need to investigate makespan max...
        ckpt_list = [0]
        for W, vals in self.ckpt_schedule.items():
            maxdict[W] = max(vals)

        
        while True:
            c = ckpt_list[-1]
            next_ckpt = c + maxdict[c]
            if next_ckpt > self.job_len:
                return ckpt_list 
            ckpt_list.append(next_ckpt)
            
        return ckpt_list

    ##################################################
    
    def Young_Daly_Estimate(self):
        C = self.C
        MTTF = self.MTTF 
        tau = math.sqrt(2.0*C*MTTF)
        exp_t = job_len*(1.0 + ((0.5*tau)/MTTF) + (C/tau))
        return (tau, exp_t)

    ##################################################

    def P_success(self, twindow, start_time):
        """ P that there is NO failure for twindow time, given the time when we started the job """
        #twindow is really job length.... 
        if self.faildist is "expon":
            psuc = max(0, 1.0-(twindow/self.MTTF))
            return math.pow(psuc, self.Num_servers)
        
        elif self.faildist is "CDF":
            return self.P_success_CDF(twindow, start_time)
        #return P_success_empirical(twindow, start_time)

    def SJK_CDF(self, t):
        A = self.cdfparam['A']
        tau1 = self.cdfparam['tau1']
        tau2 = self.cdfparam['tau2']
        b = self.cdfparam['b']
        return A*(1.0-np.exp(-t/tau1) + np.exp((t-b)/tau2))

        
    def P_success_CDF(self, twindow, start_time):
        """ Use an empirically fitted CDF for smoother fitting """
        left_idx = start_time + self.job_start_time
        right_idx = start_time + self.job_start_time + twindow
        
        pfail = self.SJK_CDF(right_idx/60.0) - self.SJK_CDF(left_idx/60.0)
        # TODO : Replace by 5-parameter CDF and make time/hours/minutes consistent. 
        psuc = max(0, 1.0-pfail)
        return math.pow(psuc, self.Num_servers)

    ##################################################

    ######################################################################

    def T_lost(self, twindow, start_time):
        """ Expected computing time lost due to failure. """
        #Not sure if applies for non memoryless. OK approximation for small twindows though.
        return twindow/2.0

    ######################################################################

    def get_solution(self, W, nofail, Wdone):
        """ Using a dictionary for storing Dynamic programming solutions.
        Should be using a 3-d np.array, but whatevs"""
        try:
            ret = self.soldict[(W, nofail, Wdone)]
        except:
            ret = None
        return ret

    def set_solution(self, W, nofail, Wdone, best, chunksize):
        self.soldict[(W, nofail, Wdone)] = (best, chunksize)
    
    ######################################################################

    def add_ckpt_schedule(self, W, chunksize):
        """ W: Work done so far. chunksize = checkpoint interval 
        """
        try:
            self.ckpt_schedule[W].append(chunksize)
        except:
            self.ckpt_schedule[W] = [chunksize]
    
    ##################################################

    def Exp_runtime(self):
        return self.soldict[(self.job_len, 0, 0)][0]

    ##################################################
        
    def makespan(self, W, nofail, Wdone, start_time, recursion_level):
        """ This is the primary function.
        Dynamic programming based calculation of E[makespan].
        Returns tuple of best and chunksize """ 
        #
        C = self.C
        R = self.R
        
        chunksize = 0
        
        if W == 0:
            #set_solution(W, nofail, Wdone, W, 0)
            return (0, 0)
        
        ret = self.get_solution(W, nofail, Wdone)
        #print("get soln " + str((W, nofail, Wdone)) + '--> ' + str(ret))
        
        if ret is not None:
            return ret
        
        best = np.inf
        t = Wdone

        #Take a checkpoint at i 
        for i in range(1, W+1):
            #print("i="+str(i))
            #print(str((W, Wdone))+" Spawning success:" + str((W-i, Wdone+i+C)))
            #Expected success, not exponential 
            exp_success, future_ckpt_interval = self.makespan(W-i, nofail, Wdone+i+C, start_time, recursion_level + 1)
            #print(str((W, Wdone))+" Got exp success="+str(exp_success))
            
            psuc = self.P_success(i + C, t)
            pfail = 1.0 - psuc
            
            if int(Wdone) != int(R):
                exp_fail, fail_future_ckpt_interval = self.makespan(W, 0, R, start_time, recursion_level + 1)
                curr = (psuc * (i + C + exp_success)) + ((1.0 - psuc) * (self.T_lost(i + C, t) + R + exp_fail))
                
            else:
                #This is to prevent infinite loops and handles the first timestep when no work has been done 
                exp_fail = 0
                if psuc != 0:
                    scaled_pfail = pfail/psuc
                else:
                    scaled_pfail = pfail
                curr = (psuc * (i + C + exp_success)) + (scaled_pfail * (self.T_lost(i + C, t) + R + exp_fail))
                    
                    #print(str((W, Wdone))+" Curr="+str(curr))

            if curr < W:
                #This should not happen, but it still does?
                #print("W={}, Wdone={}, i={}, ESUCC={}, EFAIL={}, psuc={}, Curr={}".format(\
                    #        W, Wdone, i, exp_success, exp_fail, psuc, curr))
                #This should atleast be W, this should do for now
                curr = W
                
            if curr < i:
                print("Estimate is less than i. FATAL")
                
            if curr < best : #or i==1: #Min quantum
                #print("FOUND A BEST at i="+str(i))
                best = curr
                chunksize = i
                #We need to save this somewhere....
                #print(str((W,Wdone))+" Setting soln")

        
        self.add_ckpt_schedule(Wdone, chunksize)
                
        self.set_solution(W, nofail, Wdone, best, chunksize)
        
        return self.get_solution(W, nofail, Wdone)


    ##################################################
    

# def find_nearest(array, value):
#     """ Maybe numpy has a built in for this? I always forget """
#     idx = np.searchsorted(array, value, side="left")
#     if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
#         return idx-1
#     else:
#         return idx

# ######################################################################


# def sinh_CDF(t):
#     """ Magic params hah """ 
#     R = 1.22083*10**-6
#     t0 = 12.2482
#     tau = 0.910722
#     C = 0.363843
#     return R*np.sinh((t-t0)/tau) + C




# def P_success_empirical(twindow, start_time):
#     """ From empirically observed preemptions,
#     find P(success in start_time to start_time+twindow) """
#     #TODO: Use the sinh CDF 
#     left_idx = np.searchsorted(gcp_cdf.x, start_time+job_start_time, side="left")
#     #find_nearest(gcp_cdf.x, start_time+job_start_time)
#     right_idx = np.searchsorted(gcp_cdf.x, start_time+twindow+job_start_time, side="right")
#     #find_nearest(gcp_cdf.x, start_time+twindow+job_start_time)
#     if right_idx==left_idx:
#         right_idx = right_idx + 1

#     cdf_left = gcp_cdf.y[left_idx]
#     cdf_right = gcp_cdf.y[right_idx]
#     #print(str((left_idx, right_idx, cdf_left, cdf_right)))
#     pfail = cdf_right-cdf_left
#     psuc = max(0, 1.0-pfail)
#     return math.pow(psuc, Num_servers)





######################################################################

# def dp_driver(W=100):
#     global job_len 
#     job_len = W 
#     makespan(W, 1, 0, 1*60)
#     pprint.pprint(soldict)

######################################################################

if __name__ == "__main__":
    #sys.setrecursionlimit(100000000)
    #everything is in minutes.... 
    dp = DPCkpt(job_len=169, job_start_time=21*60)
    dp.get_raw_sol_table()
    pprint.pprint(dp.dp_table)
    pprint.pprint(dp.get_checkpoint_schedule())
    #dp_driver()
    #print(P_success_CDF(60,60))

######################################################################
