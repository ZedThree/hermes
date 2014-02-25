import paramiko
import matplotlib.pyplot as plt
import numpy as np
import re

def ssh_setup():
    """
    Setup the ssh connection.
    Uses the keys found in ~/.ssh to connect to a supercomputer (currently
    hard-coded to be hpcff).
    """
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('hpcff.fz-juelich.de',username='fsggst01')

    return ssh

def get_running_jobs(ssh):
    """
    Find the running jobs on a machine using the connection SSH.
    """
    # Finds the list of running jobs for the user
    stdin, stdout, stderr = ssh.exec_command("showq | grep fsggst01 | grep Run")
    # Parses the output of the previous command into a list of running jobs
    jobs = stdout.read().splitlines()

    return jobs

def get_jobfile(ssh, jobid):
    """
    From the connection SSH, find the directory of running job JOBID.
    """
    # We need to find the directory the job is running in
    # To do this, we look for everything between 'PBS_O_WORKDIR' and 'etime' in the output of qstat -f
    # The last line is not needed, so delete it, and then remove newlines and tabs
    # The job directory is now whatever is on the right hand side of the equals sign
    stdin, stdout, stderr = ssh.exec_command("qstat -f "+ job + " | sed -n '/PBS_O_WORKDIR/,/etime/p' | sed '$d' | grep -v etime | tr -d ' \n\t' | awk -F'=' '{print $2}'")
    # We need to parse the output of the previous command
    jobdir = stdout.read().splitlines()
    # Get the filename of the text output
    stdin, stdout, stderr = ssh.exec_command("ls " + jobdir[0] + "/*.o")
    # need someway to catch the inevitable errors
    filename = stdout.read().splitlines()

    return filename

def get_energy(ssh, filename):
    """
    From the connection SSH, return the energy in FILENAME
    """
    # Pull out the field energy from the output
    stdin, stdout, stderr = ssh.exec_command("grep field\(1 " + filename[0] + " | awk '{print $7}'")
    # Parse it nicely
    energy = stdout.read().splitlines()

    return energy

def get_time(ssh, filename):
    """
    From the connection SSH, return the time of each timestep in FILENAME.
    """
    # Find the time
    stdin, stdout, stderr = ssh.exec_command("grep ^STEP " + filename[0] + " | awk '{print $6}'")
    # Parse it nicely
    time = stdout.read().splitlines()

    # Bad formatting in NEMORB means we have to delete some text from the time column
    field = re.compile('Efield\(1,1\)')
    time = [re.sub("Efield\(1,1\)","",times) for times in time]

    return time

def fit_energy(time, energy):
    """
    Fit an exponential to the energy
    """

    energylog = np.log(np.array(energy, 'float'))
    fit = np.polyfit(np.array(time,'float'),energylog,1)
    energy_fit = np.exp(np.array(time,'float')*fit[0] + fit[1])

    return energy_fit

if __name__ == "__main__":
    # Connect to a computer
    ssh = ssh_setup()
    # Find out the running jobs
    jobs = get_running_jobs(ssh)
    # Output will look something like:
    # ['2129961            fsggst01    Running  4096     3:16:38  Thu Oct 25 14:45:06']
    print jobs

    for job in jobs:
        # The job ID is just the first bit of the jobs output
        jobid = jobs[0].split()[0]
        # Find where the job is running
        filename = get_jobfile(ssh, jobid)
        # Get the field energy and time of each running job
        energy = get_energy(ssh, filename)
        time = get_time(ssh, filename)
        # Get a fit
        energy_fit = fit_energy(time, energy)
        # Plot it nicely
        plt.semilogy(time,energy,time,energy_fit,'--r')
        plt.ylabel('Energy [$m_i c_s^2$]')
        plt.xlabel('Time [$\Omega_{ci}^{-1}$]')
        plt.show()
