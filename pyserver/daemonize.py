"""Daemonize a python program
references:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
http://www.erlenstar.demon.co.uk/unix/faq_toc.html
Advanced Programming in the Unix Environment: W. Richard Stevens
"""
import os
import sys
import signal
import resource

# set the daemon umask, working directory and max # file descriptors
UMASK = 0
WORKDIR = "/"
MAXFD = 1024

# redirect standard output to /dev/null
if (hasattr(os, "devnull")):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"


def Daemonize():
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    try:
        pid = os.fork()
    except OSError, e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if (pid == 0):
        os.setsid()
        # igore SIGHUP?
        #signal.signal(signal.SIGHUP, signal.SIG_IGN)

        try:
            pid = os.fork()
        except OSError, e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if (pid == 0):
            os.chdir(WORKDIR)
            os.umask(UMASK)
        else:
            os._exit(0)
    else:
        os._exit(0)

    # set the maximum number of file descriptors
    #--------------------------------------------------
    # try:
    #        maxfd = os.sysconf("SC_OPEN_MAX")
    # except (AttributeError, ValueError):
    #        maxfd = MAXFD
    #--------------------------------------------------
    # if (os.sysconf_names.has_key("SC_OPEN_MAX")):
    #        maxfd = os.sysconf("SC_OPEN_MAX")
    # else:
    #        maxfd = MAXFD
    #--------------------------------------------------
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
    #--------------------------------------------------

    # close the file descriptors
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass

    # redirect IO
    os.open(REDIRECT_TO, os.O_RDWR)        # standard input    (0)
    os.dup2(0, 1)                        # standard output (1)
    os.dup2(0, 2)                        # standard error    (2)

    return(0)
