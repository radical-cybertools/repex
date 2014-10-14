"""
.. module:: radical.repex.md_kernles_tex.amber_kernels_tex.amber_kernel_tex_scheme_4
.. moduleauthor::  <antons.treikalis@rutgers.edu>
.. moduleauthor::  <haoyuan.chen@rutgers.edu>
"""

__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__ = "MIT"

import os
import sys
import time
import math
import json
import random
import shutil
import datetime
from os import path
import radical.pilot
from kernels.kernels import KERNELS
from replicas.replica import Replica
from amber_kernel_tex import *
import amber_kernels_tex.amber_matrix_calculator_scheme_4

#-----------------------------------------------------------------------------------------------------------------------------------

class AmberKernelTexScheme4(AmberKernelTex):
    """This class is responsible for performing all operations related to Amber for RE scheme 4.
    TODO....

    """
    def __init__(self, inp_file,  work_dir_local):
        """Constructor.

        Arguments:
        inp_file - package input file with Pilot and NAMD related parameters as specified by user 
        work_dir_local - directory from which main simulation script was invoked
        """

        AmberKernelTex.__init__(self, inp_file, work_dir_local)

        try:
            self.cycle_time = int(inp_file['input.MD']['cycle_time'])
        except:
            self.cycle_time = 3

#-----------------------------------------------------------------------------------------------------------------------------------

    def prepare_replicas_for_md(self, replicas):
        """Prepares all replicas for execution. In this function are created CU descriptions for replicas, are
        specified input/output files to be transferred to/from target system. Note: input files for first and 
        subsequent simulation cycles are different.

        Arguments:
        replicas - list of Replica objects

        Returns:
        compute_replicas - list of radical.pilot.ComputeUnitDescription objects
        """
        compute_replicas = []
        for r in range(len(replicas)):
            self.build_input_file(replicas[r])
            input_file = "%s_%d_%d.mdin" % (self.inp_basename, replicas[r].id, (replicas[r].cycle-1))

            # this is not transferred back
            output_file = "%s_%d_%d.mdout" % (self.inp_basename, replicas[r].id, (replicas[r].cycle-1))

            new_coor = replicas[r].new_coor
            new_traj = replicas[r].new_traj
            new_info = replicas[r].new_info

            old_coor = replicas[r].old_coor
            old_traj = replicas[r].old_traj

            if replicas[r].cycle == 1:
                cu = radical.pilot.ComputeUnitDescription()
                crds = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_coordinates
                parm = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_parameters
                rstr = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_restraints

                cu.executable = self.amber_path
                cu.pre_exec = self.pre_exec
                cu.mpi = self.replica_mpi
                cu.arguments = ["-O", "-i ", input_file, "-o ", output_file, "-p ", self.amber_parameters, "-c ", self.amber_coordinates, "-r ", new_coor, "-x ", new_traj, "-inf ", new_info]
                cu.cores = self.replica_cores
                cu.input_staging = [str(input_file), str(crds), str(parm), str(rstr)]
                #cu.output_staging = [str(new_coor), str(new_traj), str(new_info)]
                compute_replicas.append(cu)
            else:
                cu = radical.pilot.ComputeUnitDescription()
 
                old_output_file = "%s_%d_%d.rst_%d" % (self.inp_basename, replicas[r].id, (replicas[r].cycle-2), int(replicas[r].stopped_run) )
                
                ##################################
                # changing old path from absolute 
                # to relative so that Amber can 
                # process it
                ##################################
                path_list = []
                for char in reversed(replicas[r].old_path):
                    if char == '/': break
                    path_list.append( char )

                modified_old_path = ''
                for char in reversed( path_list ):
                    modified_old_path += char

                modified_old_path = '../' + modified_old_path.rstrip()

                ##################################
                # changing first path from absolute 
                # to relative so that Amber can 
                # process it
                ##################################
                path_list = []
                for char in reversed(replicas[r].first_path):
                    if char == '/': break
                    path_list.append( char )

                modified_first_path = ''
                for char in reversed( path_list ):
                    modified_first_path += char

                modified_first_path = '../' + modified_first_path.rstrip()


                print "Stopped i run for replica %d is: %d" % (replicas[r].id, replicas[r].stopped_run)
                restart_file = modified_old_path + "/" + old_output_file
                print "Restart file for replica %d is %s" % (replicas[r].id, restart_file)

                first_amber_parameters = modified_first_path + "/" + self.amber_parameters

                crds = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_coordinates
                parm = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_parameters
                rstr = self.work_dir_local + "/" + self.inp_folder + "/" + self.amber_restraints
                cu.executable = self.amber_path
                cu.pre_exec = self.pre_exec
                cu.mpi = self.replica_mpi
                cu.arguments = ["-O", "-i ", input_file, "-o ", output_file, "-p ", first_amber_parameters, "-c ", restart_file, "-r ", new_coor, "-x ", new_traj, "-inf ", new_info]
                
                cu.cores = self.replica_cores
                cu.input_staging = [str(input_file)]
                #cu.output_staging = [str(new_coor), str(new_traj), str(new_info)]
                compute_replicas.append(cu)

        return compute_replicas

#-----------------------------------------------------------------------------------------------------------------------------------

    def prepare_replicas_for_exchange(self, replicas):
        """Creates a list of ComputeUnitDescription objects for exchange step on resource.
        Number of matrix_calculator_s2.py instances invoked on resource is equal to the number 
        of replicas. 

        Arguments:
        replicas - list of Replica objects

        Returns:
        exchange_replicas - list of radical.pilot.ComputeUnitDescription objects
        """

        exchange_replicas = []
        for r in range(len(replicas)):
           
            # name of the file which contains swap matrix column data for each replica
            matrix_col = "matrix_column_%s_%s.dat" % (r, (replicas[r].cycle-1))
            basename = self.inp_basename
            cu = radical.pilot.ComputeUnitDescription()
            cu.executable = "python"
            # each scheme has it's own calculator!
            calculator_path = os.path.dirname(amber_kernels_tex.amber_matrix_calculator_scheme_4.__file__)
            calculator = calculator_path + "/amber_matrix_calculator_scheme_4.py" 
            cu.input_staging = [str(calculator)]
            cu.arguments = ["amber_matrix_calculator_scheme_4.py", replicas[r].id, (replicas[r].cycle-1), len(replicas), basename]
            cu.cores = 1            
            cu.output_staging = [str(matrix_col)]
            exchange_replicas.append(cu)

        return exchange_replicas

