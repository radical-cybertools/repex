"""
.. module:: radical.repex.md_kernels.amber_kernels_salt.amber_matrix_calculator_pattern_b
.. moduleauthor::  <haoyuan.chen@rutgers.edu>
.. moduleauthor::  <antons.treikalis@rutgers.edu>
"""

__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__ = "MIT"

import os
import sys
import os,sys,socket,time
from subprocess import *
import subprocess



#-----------------------------------------------------------------------------------------------------------------------------------

def call_amber(amber_path, mdin, prmtop, crd, mdinfo):

    # calling amber
    commands = []
    cmd = amber_path + ' -O -i ' + mdin + ' -p ' + prmtop + ' -c ' + crd + ' -inf ' + mdinfo
    commands.append(cmd)

    processes = [Popen(cmd, subprocess.PIPE, shell=True)  for cmd in commands]
    for p in processes: p.wait()


#-----------------------------------------------------------------------------------------------------------------------------------

def reduced_energy(temperature, potential):
    """Calculates reduced energy.

    Arguments:
    temperature - replica temperature
    potential - replica potential energy

    Returns:
    reduced enery of replica
    """
    kb = 0.0019872041    #boltzmann const in kcal/mol
    if temperature != 0:
        beta = 1. / (kb*temperature)
    else:
        beta = 1. / kb     
    return float(beta * potential)

#-----------------------------------------------------------------------------------------------------------------------------------

def get_historical_data(history_name):
    """Retrieves temperature and potential energy from simulation output file .history file.
    This file is generated after each simulation run. The function searches for directory 
    where .history file recides by checking all computeUnit directories on target resource.

    Arguments:
    history_name - name of .history file for a given replica. 

    Returns:
    data[0] - temperature obtained from .history file
    data[1] - potential energy obtained from .history file
    path_to_replica_folder - path to computeUnit directory on a target resource where all
    input/output files for a given replica recide.
       Get temperature and potential energy from mdinfo file.

    ACTUALLY WE ONLY NEED THE POTENTIAL FROM HERE. TEMPERATURE GOTTA BE OBTAINED FROM THE PROPERTY OF THE REPLICA OBJECT.
    """
    home_dir = os.getcwd()
    os.chdir("../")

    # getting all cu directories
    replica_dirs = []
    for name in os.listdir("."):
        if os.path.isdir(name):
            replica_dirs.append(name)    

    temp = 0.0    #temperature
    eptot = 0.0   #potential
    for directory in replica_dirs:
         os.chdir(directory)
         try:
             f = open(history_name)
             lines = f.readlines()
             f.close()
             path_to_replica_folder = os.getcwd()
             for i in range(len(lines)):
                 #if "TEMP(K)" in lines[i]:
                 #    temp = float(lines[i].split()[8])
                 if "EPtot" in lines[i]:
                     eptot = float(lines[i].split()[8])
             #print "history file %s found!" % ( history_name ) 
         except:
             pass 
         os.chdir("../")
 
    os.chdir(home_dir)
    return eptot, path_to_replica_folder

#-----------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    """This module calculates one swap matrix column for replica and writes this column to 
    matrix_column_x_x.dat file. 
    """

    argument_list = str(sys.argv)
    replica_id = str(sys.argv[1])
    replica_cycle = str(sys.argv[2])
    replicas = int(str(sys.argv[3]))
    base_name = str(sys.argv[4])

    # INITIAL REPLICA TEMPERATURE:
    init_temp = str(sys.argv[5])

    # AMBER PATH ON THIS RESOURCE:
    amber_path = str(sys.argv[6])

    # SALT CONCENTRATION FOR THIS REPLICA
    salt_conc = str(sys.argv[7])

    # PATH TO SHARED INPUT FILES (to get ala10.prmtop)
    shared_path = str(sys.argv[8])    

    # FILE ala10_remd_X_X.rst IS IN DIRECTORY WHERE THIS SCRIPT IS LAUNCHED AND CEN BE REFERRED TO AS:
    new_coor = "%s_%s_%s.rst" % (base_name, replica_id, replica_cycle)

    pwd = os.getcwd()
    matrix_col = "matrix_column_%s_%s.dat" % ( replica_id, replica_cycle ) 

    # getting history data for self
    history_name = base_name + "_" + replica_id + "_" + replica_cycle + ".mdinfo"
    #print "history name: %s" % history_name
    replica_energy, path_to_replica_folder = get_historical_data( history_name )

    # getting history data for all replicas
    # we rely on the fact that last cycle for every replica is the same, e.g. == replica_cycle
    # but this is easily changeble for arbitrary cycle numbers
    temperatures = [0.0]*replicas   #need to pass the replica temperature here
    energies = [0.0]*replicas

    # call amber to run 1-step energy calculation
    for j in range(replicas):
        energy_history_name = base_name + "_" + str(j) + "_" + replica_cycle + "_energy.mdinfo"
        #input_name = self.work_dir_local + "/amber_inp/" + "ala10.mdin"
        input_name = "ala10.mdin"    #temporary
        #input_name = base_name + "_" + str(j) + "_" + replica_cycle + ".mdin"
        energy_input_name = base_name + "_" + str(j) + "_" + replica_cycle + "_energy.mdin"

        f = file(input_name,'r')
        input_data = f.readlines()
        f.close()

        # change nstlim to be zero
        f = file(energy_input_name,'w')
        for line in input_data[:-3]:  #quick hack to get rid of the rstr stuff to avoid further file transfer issue--get it working first
            if "@nstlim@" in line:
                f.write(line.replace("@nstlim@","0"))
            elif "@salt@" in line:
                f.write(line.replace("@salt@",salt_conc))
            else:
                f.write(line)
        f.close()
        
        #problems here
        call_amber(amber_path, energy_input_name, shared_path + '/' + input_name.replace("mdin","prmtop") , new_coor, energy_history_name)

    for j in range(replicas):
        try:
            rj_energy, path_to_replica_folder = get_historical_data( energy_history_name )
            temperatures[j] = float(init_temp)
            energies[j] = rj_energy
        except:
             pass 

    # init swap column
    swap_column = [0.0]*replicas

    for j in range(replicas):        
        swap_column[j] = reduced_energy(temperatures[j], replica_energy)

    # printing replica id
    print str(replica_id).rstrip()
    # printing swap column
    for item in swap_column:
        print item,

    # printing path
    print str(path_to_replica_folder).rstrip()
