#!/usr/bin/python

'''
' Created on 2017-12-15
'
' find Nagios installDirectory
'
'''
import commands
import re
import sys

def find_nagiosdir():
    '''return nagios directory'''
    cmd = "ps ax -o command | grep -E 'icinga.cfg|nagios.cfg' | grep -v 'grep'"
    procs = commands.getoutput(cmd)
    if re.search('(/[^ ]+)/bin/nagios', procs):
        nagiosdir = re.search('(/.+)/bin/nagios', procs).group(1)
        return nagiosdir
    else:
        sys.exit(0)
