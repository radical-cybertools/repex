#RepEX: Replica Exchange simulations Package

This package is aimed to provide functionality to run Replica Exchange simulations using various RE schemes and MD kernels. Currectly RepEX uses NAMD as it's application kernel and allows to perform RE simulations on local and remote systems. As of now only one scheme is supported - temperature exchange, where exchange step is synchronous - all replicas must finish current cycle and then participate in exchange step. No simulation (MD) runs are performed while exchange step is happening. Exchange probability in this scheme is determined using Gibbs sampling.        

###Theory of Replica Exchange simulations

In Parallel Tempering (Replica Exchange) simulations N replicas of the original system are used to model phenomenon of interest. Typically, each replica can be treated as an independent system and would be initialised at a different temperature. While systems with high temperatures are very good at  sampling large portions of phase space, low temperature systems often become trapped in local energy minima during the simulation. Replica Exchange method is very effective in addressing this issue and generally demonstrates a very good sampling. In RE simulations, system replicas of both higher and lower temperature sub-sets are present. During the simulation they exchange full configurations at different temperatures, allowing lower temperature systems to sample a representative portion of phase space.


##Installation instructions

```bash
$ virtualenv $HOME/myenv 
$ source $HOME/myenv/bin/activate 
$ git clone https://github.com/radical-cybertools/ReplicaExchange.git 
$ cd ReplicaExchange
$ python setup.py install
```

Then you can verify that Radical Pilot was installed correctly:
```bash
$ radicalpilot-version
```

This should print Radical Pilot version in terminal
 
##Usage

###Local simulation example

![alt tag](https://github.com/radical-cybertools/ReplicaExchange/images/Scheme_s2.jpg)


First, you need to change several input parameters required to run RE simulation on local system. Instructions on how to do this are specified in /src/radical/repex/config/config.info file.

To run RE simulation, you need to pass simulation configuration file as a command line argument. In order to run provided RE example execute the following commands in terminal: 

```bash
$ cd src/radical/repex
$ python launch_simulation.py --input='config/input.json'
```

This will run RE temperature exchange simulation involving 6 replicas on your local system. Simulation will perform a total of 2 cycles performing one temperature exchange step. During the simulation input files for each of the replicas will be generated. After simulation is done in ReplicaExchange/src/radical/repex/ directory you should see six new "replica_x" directories. Each directory will contain simulation output files.  

###Remote (Stampede) simulation example

In order to run this example you don't need to login to Stampede, but you need to have a password-less ssh to Stampede configured.
Instructions on how to do this can be found at: http://www.linuxproblem.org/art_9.html. Then, you need to change several input parameters required to run RE simulation on Stampede. These can be found in /src/radical/repex/config/config.info file. 


To run RE simulation, you need to pass simulation configuration file as a command line argument. In order to run RE simulation execute the following commands in terminal:  

```bash
$ cd src/radical/repex
$ python launch_simulation.py --input='config/input.json'
```

This will run RE temperature exchange simulation involving 16 replicas on Stampede remotely. Simulation will perform a total of 2 cycles performing one temperature exchange step. During the simulation input files for each of the replicas will be transferred to your local system. After simulation is done in ReplicaExchange/src/radical/repex/ directory you should see 12 new "replica_x" directories. Each directory will contain simulation output files.  

###input.json 

**input.PILOT**

In this part of input file must be specified Pilot releted paramers. 

- resource: name of the system to use 

- sandbox: working directory for ComputePilot on target resource

- cores: number of cores the pilot should allocate on the target resource 

- runtime: estimated total run time (wall-clock time) in minutes of the ComputePilot

- cleanup: boolean variable to specify if ComputeUnit and ComputePilot directories should be deleted or not  

**input.NAMD**

In this part of json input file must be specified NAMD related paramers. 

- input_folder: folder where all namd input files reside, e.g. .psf, .pdb, .params

- input_file_basename: base name of NAMD input file (.namd); this file is used to create individual input files for replicas 

- namd_structure: name of namd structure file (.psf), this file must reside in input_folder

- namd_coordinates: name of namd coordinates file (.pdb), this file must reside in input_folder

- namd_parameters: name of namd parameters file (.params), this file must reside in input_folder

- number_of_replicas: number of replicas to be launched on a target resource 

- min_temperature: minimum temperature for replicas

- max_temperature: maximum temperature for replicas  

- steps_per_cycle: number of steps each replica performs in one cycle

- number_of_cycles: number of cycles to perform during simulation

All other parameters must be specified in NAMD input file directly!




