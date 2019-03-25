## Creating the SSH keys
* ssh-keygen -t rsa -f ~/.ssh/[KEY_FILENAME] -C [USERNAME]
* download the public key and upload that to Metadata -> sshkeys
* Then, ssh -i [Path to private key] localhost

## Setting up gcloud API
* gcloud auth application-default login

## git clone the project
* git clone https://github.com/prateek-s/scispot.git
* sudo rm /var/lib/slurm-llnl/slurmctld/clustername

## Install the dependancies
* sudo apt-get install python-pip 
* sudo pip install Twisted
* sudo pip install requests
* sudo pip install tinydb
* sudo pip install --upgrade google-api-python-client
* sudo pip install paramiko
* sudo pip install python-dateutil

## copy the evlisten_copy.p and edit
* cp ~/scispot/code/evlisten.p ~/scispot/code/evlisten_copy.p
* Overide the following
  * username = 'kadupitiya'
  * key_filename = '/home/kadupitiya/.ssh/google_key'
  * zone = 'us-central1-c'
 
 ## change the handle_fin.sh and handle_fail.sh file endpoints
 * curl "http://156.56.159.51:7878/?preempted=$jobid" to curl "http://localhost:7878/?preempted=$jobid"
 * curl "http://156.56.159.51:7878/?finished=$jobid" to curl "http://localhost:7878/?finished=$jobid"
 
 ## Run the program
 * One CMD: python ~/scispot/code/evlisten_copy.py
 * Second CMD: curl "http://localhost:7878/?explore=True&target_cpus=16"
 * http://localhost:7878/?preempted=abacus
 * http://localhost:7878/?finished=jobid
 * http://localhost:7878/?launch_cluster=True&namegrp=abra&num_nodes=4&mtype=n1-highcpu-16&start_id=1&slurm_master=ubslurm1
 
 ## slurm commands
 * /var/log/slurm-lln
 * sinfo 
 * squeue
 * sbatch -N 1 -c 8 -n 1 /scispot/sb_confinement.sh
 * scancel jobid

