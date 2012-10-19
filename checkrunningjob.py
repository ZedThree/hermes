import paramiko
import matplotlib.pyplot as plt

if __name__ == "__main__": 
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('hpcff.fz-juelich.de',username='fsggst01')
    stdin, stdout, stderr = ssh.exec_command("showq | grep fsggst01 | grep Run")
    
    jobs = stdout.read().splitlines()
    print jobs
    
    for job in jobs:
        stdin, stdout, stderr = ssh.exec_command("qstat -f "+ job + " | sed -n '/PBS_O_WORKDIR/,/etime/p' | sed '$d' | grep -v etime | tr -d ' \n\t' | awk -F'=' '{print $2}'")
        jobdir = stdout.read().splitlines()
        print jobdir
        stdin, stdout, stderr = ssh.exec_command("ls " + jobdir[0] + "/*.o")
    # need someway to catch the inevitable errors
        filename = stdout.read().splitlines()
        print filename
        stdin, stdout, stderr = ssh.exec_command("grep field\(1 " + filename[0] + " | awk '{print $7}'")
        data = stdout.read().splitlines()
        plt.semilogy(data)
        plt.show()
