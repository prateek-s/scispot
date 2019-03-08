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

""" 
Usage: http://localhost:7878/?preempted=abacus
http://localhost:7878/?finished=jobid 
""" 


##################################################    ##################################################

class evlisten(resource.Resource):
    isLeaf = True  # Required by twisted?

    ##################################################

    def __init__(self):
        #Open the job and vmdb json databases? 
        pass
    
    ##################################################
    
    def get_jobdb(self):
        return tinydb.TinyDB('jobdb.json')

    def get_vmdb(self):
        return tinydb.TinyDB('vmdb.json')
    
    ##################################################
    
    def handle_finished(self, jobids):
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
                print("No matching job")
                jobdb.insert({'jobid':job, 't_finish':fin_time})
            else:
                jobdb.update({'t_finish':fin_time}, q.jobname == job)
                
        jobdb.close() #For mutual exclusion     
        return 

    ##################################################
    
    def handle_preempted(self, vmnames):
        if vmnames is None or len(vmnames) is 0:
            print("empty vnames list, nothing to do")
            return
        
        fin_time = datetime.datetime.now().isoformat()
        vmdb = self.get_vmdb()

        for vm in vmnames:
            q = tinydb.Query()
            res = vmdb.search(q.vmname == vm)
            if len(res) is 0:
                print("VM not found?")
                vmdb.insert({'vmname':vm, 't_finish':fin_time})
            else:
                vmdb.update({'t_finish':fin_time, 'status':'preempted'}, q.vmname == vm)

        vmdb.close()
        return

    ##################################################
    
    def parse_handle_req(self, req_args):
        if 'preempted' in req_args.keys():
            print("preempted")
            #Get the node id
            vals = req_args['preempted']
            self.handle_preempted(vals)
            
        elif 'finished' in req_args.keys():
            #Get the job id
            print("finished")
            vals = req_args['finished']
            self.handle_finished(vals)
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
