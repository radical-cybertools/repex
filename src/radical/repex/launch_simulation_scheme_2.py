"""
.. module:: radical.repex.namd_kernels.launch_simulation
.. moduleauthor::  <antons.treikalis@rutgers.edu>
"""

__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__ = "MIT"

import os
import sys
import math
import time
import json
import optparse
from os import path
import radical.pilot
from replicas.replica import Replica
from repex_utils.replica_cleanup import *
from repex_utils.parser import parse_command_line
from namd_kernels.namd_kernel_scheme_2 import NamdKernelScheme2
from pilot_kernels.pilot_kernel_scheme_2 import PilotKernelScheme2
    
#-----------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    """Runs RE simulation using scheme 2. 

    RE scheme 2:
    - Synchronous RE scheme: none of the replicas can start exchange before all replicas has finished MD run.
    Conversely, none of the replicas can start MD run before all replicas has finished exchange step. 
    In other words global barrier is present.   
    - Number of replicas is greater than number of allocated resources for both MD and exchange step.
    - Simulation cycle is defined by the fixed number of simulation time-steps for each replica.
    - Exchange probabilities are determined using Gibbs sampling.
    - Exchange step is performed in decentralized fashion on target resource.
    """
 
    print "*********************************************************************"
    print "*                 RepEx simulation: NAMD + RE scheme 2             *"
    print "*********************************************************************"

    work_dir_local = os.getcwd()
    params = parse_command_line()
    
    # get input file
    json_data=open(params.input_file)
    inp_file = json.load(json_data)
    json_data.close()


    # initializing kernels
    md_kernel = NamdKernelScheme2( inp_file, work_dir_local )
    pilot_kernel = PilotKernelScheme2( inp_file )

    # initializing replicas
    replicas = md_kernel.initialize_replicas()

    print "Total number of replicas: %d" % len(replicas)
    
    pilot_manager, pilot_object, session = pilot_kernel.launch_pilot()
    
    ##############################################
    # this is to make sure what pilot is running
    # needed only for performance measurements
    pilots = pilot_manager.get_pilots()
    while(str(pilots[0].state) != "PendingActive"):
        time.sleep(5)
        print "waiting for Pilot te become active..."
        print pilots[0].state
    ##############################################

    # now we can run RE simulation
    pilot_kernel.run_simulation( replicas, pilot_object, session, md_kernel )
                
    # finally we are moving all files to individual replica directories
    move_output_files(work_dir_local, md_kernel.inp_basename, replicas ) 

    session.close()
    # delete all replica folders
    #clean_up(work_dir_local, replicas )

    #sys.exit(0)

