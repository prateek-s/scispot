import os,sys,math
import pprint
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

####!! ACHTUNG. RUN using python3. Python2 gives the wrong results! WHY!?!!?!?!?!

######################################################################

C = 1 #Time it takes to write a checkpoint. 1 Minute
R = 1 #Recovery time
MTTF = 12*60
Num_servers = 1
job_start_time = 0*60

faildist= "empirical" # "empirical"
#"expon" #or empirical

fails_full=np.array([86460.7, 2363.482, 86439.649, 88954.991, 88949.557, 1245.761, 88928.863, 4810.814, 22303.542, 2392.038, 4648.701, 76766.687, 6563.444, 38889.587, 88462.394, 88456.938, 895.826, 401.218, 86488.147, 86480.014, 86474.189, 86467.604, 86462.225])/60.0

gcp_cdf=ECDF(fails_full)

job_len = None #In Minutes 

soldict=dict()

######################################################################

def Young_Daly_Estimate():
    tau = math.sqrt(2.0*C*MTTF)
    exp_t = job_len*(1.0 + ((0.5*tau)/MTTF) + (C/tau))
    return (tau, exp_t)

def find_nearest(array, value):
    """ Maybe numpy has a built in for this? I always forget """
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

######################################################################


def sinh_CDF(t):
    """ Magic params hah """ 
    R = 1.22083*10**-6
    t0 = 12.2482
    tau = 0.910722
    C = 0.363843
    return R*np.sinh((t-t0)/tau) + C


def P_success_CDF(twindow, start_time):
    """ Use an empirically fitted CDF for smoother fitting """
    left_idx = start_time + job_start_time
    right_idx = start_time + job_start_time + twindow

    pfail = sinh_CDF(right_idx/60.0) - sinh_CDF(left_idx/60.0)
    psuc = max(0, 1.0-pfail)
    return math.pow(psuc, Num_servers)


def P_success_empirical(twindow, start_time):
    """ From empirically observed preemptions,
    find P(success in start_time to start_time+twindow) """
    #TODO: Use the sinh CDF 
    left_idx = np.searchsorted(gcp_cdf.x, start_time+job_start_time, side="left")
    #find_nearest(gcp_cdf.x, start_time+job_start_time)
    right_idx = np.searchsorted(gcp_cdf.x, start_time+twindow+job_start_time, side="right")
    #find_nearest(gcp_cdf.x, start_time+twindow+job_start_time)
    if right_idx==left_idx:
        right_idx = right_idx + 1

    cdf_left = gcp_cdf.y[left_idx]
    cdf_right = gcp_cdf.y[right_idx]
    #print(str((left_idx, right_idx, cdf_left, cdf_right)))
    pfail = cdf_right-cdf_left
    psuc = max(0, 1.0-pfail)
    return math.pow(psuc, Num_servers)


def P_success(twindow, start_time):
    """ P that there is NO failure for twindow time, given the time when we started the job """
    if faildist is "expon":
        psuc = max(0, 1.0-(twindow/MTTF))
        return math.pow(psuc, Num_servers)

    elif faildist is "empirical":
        return P_success_CDF(twindow, start_time)
        #return P_success_empirical(twindow, start_time)

######################################################################

def T_lost(twindow, start_time):
    """ Expected computing time lost due to failure. """
    #Not sure if applies for non memoryless
    return twindow/2.0

######################################################################

def get_solution(W, nofail, Wdone):
    """ Using a dictionary for storing Dynamic programming solutions.
    Should be using a 3-d np.array, but whatevs"""
    try:
        ret = soldict[(W, nofail, Wdone)]
    except:
        ret = None
    return ret

def set_solution(W, nofail, Wdone, best, chunksize):
    soldict[(W, nofail, Wdone)] = (best, chunksize)

######################################################################

def makespan(W, nofail, Wdone, start_time):
    """ This is the primary function.
    Dynamic programming based calculation of E[makespan]"""
    global C
    global R

    chunksize = 0

    if W == 0:
        #set_solution(W, nofail, Wdone, W, 0)
        return (0, 0)

    ret = get_solution(W, nofail, Wdone)
    #print("get soln " + str((W, nofail, Wdone)) + '--> ' + str(ret))

    if ret is not None:
        return ret

    best = np.inf
    t = Wdone

    for i in range(1, W+1):
        #print("i="+str(i))
        #print(str((W, Wdone))+" Spawning success:" + str((W-i, Wdone+i+C)))
        exp_success = makespan(W-i, nofail, Wdone+i+C, start_time)[0]
        #print(str((W, Wdone))+" Got exp success="+str(exp_success))

        psuc=P_success(i+C, t)
        pfail=1.0-psuc

        if int(Wdone) != int(R):
            exp_fail = makespan(W, 0, R, start_time)[0]
            curr = (psuc*(i+C+exp_success))+((1.0-psuc)*(T_lost(i+C, t) + R + exp_fail))

        else:
            #This is to prevent infinite loops
            exp_fail = 0
            if psuc!=0:
                scaled_pfail = pfail/psuc
            else:
                scaled_pfail = pfail
            curr = (psuc*(i+C+exp_success))+(scaled_pfail*(T_lost(i+C, t) + R + exp_fail))

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

    #print(str((W,Wdone))+" Setting soln")
    set_solution(W, nofail, Wdone, best, chunksize)

    return get_solution(W, nofail, Wdone)

######################################################################

def dp_driver(W=100):
    global job_len 
    job_len = W 
    makespan(W, 1, 0, 1*60)
    pprint.pprint(soldict)

######################################################################

if __name__ == "__main__":
    #sys.setrecursionlimit(100000000)
    dp_driver()
    print("-----------------------------------------")
    print(Young_Daly_Estimate())
    #dp_driver()
    #print(P_success_CDF(60,60))

######################################################################
