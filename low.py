import os

import psutil


def lowpriority():
    """ Set the priority of the process to below-normal."""
    p = psutil.Process(os.getpid())
    p.nice(psutil.IDLE_PRIORITY_CLASS)