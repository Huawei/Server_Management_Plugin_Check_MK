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

# modify by fangzhengbo at 2018.02.24
# for find nagios dir through /etc/profile
def find_nagiosdir():
    '''return nagios directory'''
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)

    return procs
