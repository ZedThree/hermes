hermes
======

Checks the status of running jobs on remote machines.

Uses paramiko to ssh into a remote machine (currently hard-coded to be HPC-FF).
Then uses qstat, sed, grep and awk to find out what jobs are running, where they are outputting data, and extract the field energy from the text output.
Matplotlib is used to plot the energy against timestep on a semi-log scale.