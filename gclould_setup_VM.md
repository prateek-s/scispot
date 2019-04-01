## Creating the SSH keys
* ssh-keygen -t rsa -f ~/.ssh/[KEY_FILENAME] -C [USERNAME]
* download the public key and upload that to Metadata -> sshkeys
* Then, ssh -i [Path to private key] localhost

## Setting up gcloud API
* gcloud auth application-default login

## git clone the project
* git clone https://github.com/prateek-s/scispot.git
* sudo rm /var/lib/slurm-llnl/slurmctld/clustername : Remove two times until slurm start works
* systemctl start slurmctld

## Install the dependancies
* sudo apt-get install python-pip 
* sudo pip install Twisted
* sudo pip install requests
* sudo pip install tinydb
* sudo pip install --upgrade google-api-python-client
* sudo pip install paramiko
* sudo pip install python-dateutil
* sudo pip install numpy

* sudo pip install Twisted requests tinydb --upgrade google-api-python-client paramiko python-dateutil numpy cryptography

## copy the evlisten_copy.p and edit
* cp ~/scispot/code/evlisten.p ~/scispot/code/evlisten_copy.p
* Overide the following
  * username = 'kadupitiya'
  * key_filename = '/home/kadupitiya/.ssh/google_key'
  * zone = 'us-central1-c'
  * current_master = 'n-master-1'
  * batcmd = "sbatch --no-requeue  --parsable -N {num_nodes} -c {cores} -n {num_nodes} {runfile} {jobparams}"......
 
 ## change the handle_fin.sh and handle_fail.sh file endpointsin the VM(/scispot/) not in clone project
 * curl "http://156.56.159.51:7878/?preempted=$jobid" to curl "http://localhost:7878/?preempted=$jobid"
 * curl "http://156.56.159.51:7878/?finished=$jobid" to curl "http://localhost:7878/?finished=$jobid"
 
 ## Run the program
 * One CMD: python ~/scispot/code/evlisten.py | tee shapes_c_parellel_32_2_4.dat
 * stdbuf -o 0 python ~/scispot/code/evlisten.py | tee shapes_c_parellel_32_2_4.dat
 * Second CMD: curl "http://localhost:7878/?explore=True&target_cpus=16"
 * Second CMD: curl "http://localhost:7878/?exploit=True&num_jobs=10"
 * "http://localhost:7878/?preempted=abacus"
 * "http://localhost:7878/?finished=jobid"
 * "http://localhost:7878/?launch_cluster=True&namegrp=abra&num_nodes=4&mtype=n1-highcpu-16&start_id=1&slurm_master=ubslurm1"
 
 ## slurm commands
 * systemctl start slurmctld
 * /var/lib/slurm-llnl
 * sinfo 
 * squeue
 * sbatch -N 1 -c 8 -n 1 /scispot/sb_confinement.sh
 * scancel jobid
 * scontrol show job
 * strigger --get
 * Logfile: /var/log/slurm-llnl/slurmctld.log
 * Job log: /var/log/slurmjobs
 
 
 ## Path issues
 * sudo chmod -R 777 /scispot/*
 * sudo chmod +x /scispot/nanoconfinement-md-master/bin/
 * sudo chmod +x /scispot/np-shape-lab-master/bin/outfiles
 * mpirun --wdir /scispot/np-shape-lab-master/bin/ ./np_shape_lab $@ -S 40000
 * mpirun --wdir /scispot/nanoconfinement-md-master/bin/ ./md_simulation_confined_ions $@
 
 ## tmux cheat codes
 ### Sessions
 * CTRL B is the tmux shortcut mode
 * tmux new -s kadda
 * tmux new -s kadda
 * tmux attach -t kadda 
 * tmux switch -t kadda
 * tmux list-sessions  or tmux ls
 * tmux detach (prefix + d)
 * tmux kill-session -t kadda
 ### Windows (tabs)
 * tmux split-window or tmux split-window -v
 * tmux split-window -h
 * tmux swap-pane -[UDLR] (prefix + { or })
 * tmux select-pane -[UDLR]
 * up
 * CTRL B and then %  for horizontal
 * CTRL B and then " for vertical

###In tmux, hit the prefix ctrl+b and then:

* c           new window
* ,           name window
* w           list windows
* f           find window
* &           kill window
* .           move window - prompted for a new number
* :movew<CR>  move window to the next unused number

### Panes (splits)
* %  horizontal split
* "  vertical split

* o  swap panes
* q  show pane numbers
* x  kill pane
* ⍽  space - toggle between layouts
* Window/pane surgery
* :joinp -s :2<CR>  move window 2 into a new pane in the current window
* :joinp -t :1<CR>  move the current pane into a new pane in window 1
 
 

