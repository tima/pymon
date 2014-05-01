import sys
import subprocess
import time

from pymon.daemon import Daemon

# child catching graceful signal -- still restarts? 
# TO DO: Logging strategy

class pymon(Daemon):

    def __init__(
        self,
        cmd,
        daemonize=False,
        logfile='mon.log',
        max_attempts=10,
        sleep=1,
        pidfile=None,
        child_pidfile=None,
        on_restart=None,
        on_error=None,
        prefix=None,
        ):

        self.cmd = cmd
        super(Daemon, self).__init__(pidfile) # redirect stdin/out/err to log file here or in daemon?
        self.daemonize = daemonize
        self.logfile = logfile
        self.max_attempts = max_attempts
        self.sleep = sleep
        self.child_pidfile = child_pidfile
        self.prefix = prefix
        self.attempts = 0
        self.last_restart_at = 0
        self.clock = 60000
	self.on_restart = on_restart
	self.on_error = on_error

        # self.show_status = false

    def exec_on(self, cmd):
        '''
        A utility method for running on_error or on_restart when needed
        '''

        pid = self.readpid(pidfile=self.child_pidfile) 
        try:
            proc = subprocess.Popen([cmd, pid]) # what to do about stdin/stdout/stderr? env? bufsize=256? call or call_check?
	    (stdout, stderr) = proc.communicate()
        except (OSError, IOError), e:
            pass
        except:
            pass

    def ms_since_last_restart():
        if self.last_restart_at == 0:
	    return 0
	now = int(round(time.time() * 1000)) 
	return now - self.last_restart_at

    def attempts_exceeded(self, ms):
        self.attempts += 1
        self.clock -= ms
	if self.clock <= 0:
	    self.clock = 60000
	    self.attempts = 0
	    return False
	if monitor.attempts < self.max_attempts:
	    return False
	return True

    def run(self):
	pass
        while True:
	    child = subprocess.Popen(self.cmd) #stdin etc?
	    self.writepid(pid=child.pid, pidfile=self.child_pidfile)
	    child.wait()
	    # if signaled (any type) log and sleep
	    # if exit log and sleep
            if self.on_restart:
                self.exec_on(self.on_restart)
            # logging here
	    # self.delpid(pidfile=self.child_pidfile) # should need this if atexit does its job.
	    ms = self.ms_since_last_restart()
	    if self.attempts_exceeded(ms):
	        # logging 
	        if self.on_error:
	            self.exec_on(self.on_error)
                # more logging
                sys.exit(2)

