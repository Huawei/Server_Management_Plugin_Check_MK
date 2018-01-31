'''
'Auto Config  for Huawei Plugin
'''

###########################################################################
# Filename:              huaweiAutoConfig.py
# Version:               1.0.2
# Created:               2018-01-18
# Author:                Miya
# Description:           Check_MK plugin
# History: 
#--------------------------------------------------------------------------

from xml.dom import minidom
from datetime import datetime 

import os
import sys
import re
import commands
import logging
import logging.handlers as handlers
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACMD5AuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmDESPrivProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACSHAAuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmAesCfb128Protocol
from pysnmp.entity.rfc3413.oneliner import cmdgen

MODULES_DIR = os.path.dirname(__file__)
import find_nagois_dir 
NAGIOS_DIR = find_nagois_dir.find_nagiosdir()
if NAGIOS_DIR: 
    if not os.path.exists(NAGIOS_DIR + "/bin/huawei_server/cmkGenKey.py"):
        commands.getoutput("cp " \
                          + NAGIOS_DIR + "/bin/huawei_server/genKey.py " \
                          + NAGIOS_DIR + "/bin/huawei_server/cmkGenKey.py")
    commands.getoutput("sed -i 's?../../etc?" \
                          + NAGIOS_DIR + "/etc?g' " \
                          + NAGIOS_DIR + "/bin/huawei_server/cmkGenKey.py")
    from sys import path
    path.append(str(NAGIOS_DIR) + "/bin/huawei_server/")
    from cmkGenKey import genRootKeyStr, dencryptKey, readKey, encryptKey

if not os.path.exists(MODULES_DIR + "/cmk_base_for_huawei.py"):
    commands.getoutput("cat " \
      + MODULES_DIR \
      + "/check_mk.py  | " \
      + "sed -n '/#!\/usr\/bin\/python/,/opt_inv_fail_status = int(a)/{p}' > " \
      + MODULES_DIR + "/cmk_base_for_huawei.py")
if os.path.exists(MODULES_DIR + "/cmk_base_for_huawei.py"):
    execfile(MODULES_DIR + '/cmk_base_for_huawei.py')

# Conveniance macros for host and service rules
ALL_HOSTS = [ '@all' ]      # physical and cluster hosts
NEGATE  = '@negate'       # negation in boolean lists
GLOABLE_HOSTS = []
GLOABLE_IPS   = []

# add logs file
DATE = datetime.now()
LOGFILE = 'hwconfiguration_' + DATE.strftime('%Y-%m-%d') + '.log' 
LOGFILEERR = 'hwconfiguration_error_' + DATE.strftime('%Y-%m-%d') + '.log'
LOGGER = logging.getLogger('hwconfiguration')
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(\
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
CONSOLEHANDLER = logging.StreamHandler()
CONSOLEHANDLER.setLevel(logging.DEBUG)
LOGSFOLDER = os.path.dirname(__file__) + os.path.sep + 'logsforhuawei'
commands.getoutput("if [ ! -d " \
                    + LOGSFOLDER \
                    + " ]; then \n sudo mkdir " + LOGSFOLDER + "\n fi")
FILEHANDLER = handlers.TimedRotatingFileHandler(os.path.dirname(__file__) \
                            + os.path.sep + 'logsforhuawei' +  os.path.sep \
                                                        + LOGFILE, \
                                                        when='midnight', \
                                                        interval=1, \
                                                        backupCount=30)
FILEHANDLER.setLevel(logging.INFO)
ERRORFILEHANDLER = logging.FileHandler(os.path.dirname(__file__) \
                         + os.path.sep + 'logsforhuawei' +  os.path.sep \
                                       + LOGFILEERR)
ERRORFILEHANDLER.setLevel(logging.ERROR)
CONSOLEHANDLER.setFormatter(FORMATTER)
FILEHANDLER.setFormatter(FORMATTER)
ERRORFILEHANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLEHANDLER)
LOGGER.addHandler(FILEHANDLER)
LOGGER.addHandler(ERRORFILEHANDLER)


def checkEnv():
    '''
    ' method: checkEnv()
    ' check the environments before configure
    '''
    # check if nagios is running
    if NAGIOS_DIR is None:
        LOGGER.error("Nogios is not running,please start first")
        sys.exit()
    # check if host is monitored by cmk
    if only_hosts:
        i = 0
        ismonitor = 'Y'
        while i < len(only_hosts):
            if '!offline' in only_hosts[i][0]:
                ismonitor = 'N'
                i += 1
                break
        if ismonitor == 'Y':
            LOGGER.error("""There will be some conflicts \
about huawei server in folder,please set only_hosts in \
 /etc/check_mk/conf.d/wato/rules.mk like: only_hosts = [
( ['!offline', ], ALL_HOSTS, \
{'description': u'Do not monitor hosts with the tag "offline"'} ),
] + only_hosts""")
            sys.exit()
    else:
        LOGGER.error("""There will be some conflicts \
about huawei server in folder,please set only_hosts in \
 /etc/check_mk/conf.d/wato/rules.mk like: only_hosts = [
( ['!offline', ], ALL_HOSTS, \
{'description': u'Do not monitor hosts with the tag "offline"'} ),
] + only_hosts""")
        sys.exit()

    # check if exist SNMP Credential,if no,clean the configuration
    if len(snmp_communities) < 1:
        commands.getoutput("sudo rm -rf " \
                           + NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg")
        commands.getoutput("sudo rm -rf " \
                           + NAGIOS_DIR + "/etc/huawei_server/huawei_hosts.xml")
        commands.getoutput("sudo cp " \
                           + MODULES_DIR + "/huawei_server/huawei_hosts.xml " \
                           + NAGIOS_DIR + "/etc/huawei_server/")
        commands.getoutput("sudo cp " \
                           + MODULES_DIR + "/huawei_server/hw_server.cfg " \
                           + NAGIOS_DIR + "/etc/huawei_server/")
        commands.getoutput("sudo chown nagios.nagios " \
            + NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg")
        commands.getoutput("sudo chown nagios.nagios " \
            + NAGIOS_DIR + "/etc/huawei_server/huawei_hosts.xml")
        LOGGER.error("no found snmp credential,please create snmp credential! ")
        sys.exit()

def getRootKey():
    '''
    ' method: getRootKey(), get Huawei rootkey
    ' return rootkey
    '''
    rootkey = dencryptKey(readKey(), genRootKeyStr())
    return rootkey

def encrypt(pkey, folder):
    '''
    ' method: encrypt
    ' input:password/community,hosts folder
    ' return encryption password
    '''
    rootkey = getRootKey()
    if rootkey is None:
        sys.exit()
    # check if password is encrypted
    if 0 < len(pkey) < 44:
        encryptpwd = encryptKey(pkey, rootkey)
        # find cmk snmp rule folder,replace password with encryption password
        if folder == 'Main directory' \
        or folder == '':
            folder_dir = check_mk_configdir + "/wato/rules.mk"
            commands.getoutput("sed -i \"s?'" \
                               + pkey.replace('$', '\$') + "', 'AES',?'" \
                               + encryptpwd + "', 'AES',?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                               + pkey.replace('$', '\$') + "', 'DES',?'" \
                               + encryptpwd + "', 'DES',?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                               + pkey.replace('$', '\$') + "', 'AES')}?'" \
                               + encryptpwd + "', 'AES')}?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                               + pkey.replace('$', '\$') + "', 'DES')}?'" \
                               + encryptpwd + "', 'DES')}?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'collSNMPv2', '" \
                               + pkey.replace('$', '\$') \
                               + "'?'collSNMPv2', '" + encryptpwd + "'?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'collSNMPv1', '" \
                               + pkey.replace('$', '\$') \
                               + "'?'collSNMPv1', '" + encryptpwd + "'?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'trapSNMPv1', '" \
                               + pkey.replace('$', '\$') \
                               + "'?'trapSNMPv1', '" + encryptpwd + "'?g\" " \
                               + folder_dir)
            commands.getoutput("sed -i \"s?'trapSNMPv2', '" \
                               + pkey.replace('$', '\$') \
                               + "'?'trapSNMPv2', '" + encryptpwd + "'?g\" " \
                               + folder_dir)
        else:
            folder_dir = check_mk_configdir + "/wato/" + folder + "/rules.mk"
            commands.getoutput("sed -i \"s?'" \
                         + pkey.replace('$', '\$') + "', 'AES',?'" \
                         + encryptpwd + "', 'AES',?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                         + pkey.replace('$', '\$') + "', 'DES',?'" \
                         + encryptpwd + "', 'DES',?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                         + pkey.replace('$', '\$') + "', 'AES')}?'" \
                         + encryptpwd + "', 'AES')}?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'" \
                         + pkey.replace('$', '\$') + "', 'DES')}?'" \
                         + encryptpwd + "', 'DES')}?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'collSNMPv2', '" \
                         + pkey.replace('$', '\$') \
                         + "'?'collSNMPv2', '"  + encryptpwd + "'?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'collSNMPv1', '" \
                         + pkey.replace('$', '\$') \
                         + "'?'collSNMPv1', '" + encryptpwd + "'?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'trapSNMPv1', '" \
                         + pkey.replace('$', '\$') \
                         + "'?'trapSNMPv1', '" + encryptpwd + "'?g\" " \
                         + folder_dir)
            commands.getoutput("sed -i \"s?'trapSNMPv2', '" \
                         + pkey.replace('$', '\$') \
                         + "'?'trapSNMPv2', '" + encryptpwd + "'?g\" " \
                         + folder_dir)
        return encryptpwd
    else:
        return pkey

def getIp(ipaddr, count):
    '''
    ' Methods : getIp,getIp for ip ranges
    ' return range_ips
    '''
    count = int(count)
    ip2 = int(ipaddr.split('.')[-2])
    ip1 = int(ipaddr.split('.')[-1])
    ip_before = '%s.%s' % (ipaddr.split('.')[0], ipaddr.split('.')[1])
    range_ips = []
    for i in range(0, count):
        new_ip1 = ip1 + i
        if  1 <= new_ip1 <= 254:
            range_ips.append('%s.%s.%s' % (ip_before, str(ip2), str(new_ip1)))
    return range_ips

def snmpTest(snmpdic, ipaddress):
    '''
    ' snmp test
    ' input: snmpcredential,ipaddress
    ' output: isSucessful
    '''
    errorindication = None
    errorstatus = 0
    errorindex = 0
    varbinds = None
    testoid = '1.3.6.1.4.1.2011.2.235.1.1.19.50.1.9.1'
    authprotocol = None
    privprotocol = None
    if 'SHA' in snmpdic:
        authprotocol = usmHMACSHAAuthProtocol
    else:
        authprotocol = usmHMACMD5AuthProtocol
    if 'AES' in snmpdic:
        privprotocol = usmAesCfb128Protocol
    else:
        privprotocol = usmDESPrivProtocol

    pkey = ''
    pwd = ''
    port = ''
    if len(snmpdic) == 5:
        pkey = snmpdic[1]
        port = snmpdic[4]
    elif len(snmpdic) == 3:
        pkey = snmpdic[0]
        port = snmpdic[2]
    if pkey and len(pkey) < 44:
        pwd = pkey
    else:
        rootkey = getRootKey()
        pwd = dencryptKey(pkey, rootkey)
    if len(snmpdic) == 5:
        errorindication, errorstatus, errorindex, varbinds = \
                cmdgen.CommandGenerator().getCmd(cmdgen.UsmUserData(\
                                           snmpdic[0], \
                                           pwd, \
                                           pwd, \
                                           authprotocol, \
                                           privprotocol ), \
                                    cmdgen.UdpTransportTarget(\
                                           (ipaddress, \
                                            port), timeout = 1, retries = 2), \
                                            testoid)
    elif len(snmpdic) == 3:
        errorindication, errorstatus, errorindex, varbinds = \
                cmdgen.CommandGenerator().getCmd(
                            cmdgen.CommunityData(pwd), \
                            cmdgen.UdpTransportTarget(\
                                (ipaddress, port), timeout = 1, retries = 2), \
                                   testoid)
    issucessful = 'No'
    if errorindication is None \
                    and errorstatus == 0 \
                    and errorindex == 0 \
                    and varbinds:
        issucessful = 'Yes'
    if issucessful == 'No':
        LOGGER.error("snmp test failed,please check host:" + ipaddress)
    if issucessful == 'Yes':
        LOGGER.info("snmp test successfully for host:" + ipaddress)
    return issucessful

def getHostsFromFolder(folder, devicetypeforrule):
    '''
    ' Methods : getHostsFromFolder
    ' input: folder,devicetype,snmpdic
    ' return hostslist with devicetype
    '''
    hostlist = []
    for hostandtag in all_hosts:
        isoffline = 'No'
        devicetypeforhost = ''
        if re.search('(^[^\|]+)\|.*' + folder, hostandtag):
            host = ''
            # get the host from folder
            if re.search('(^[^\|]+)\|.*' + folder, hostandtag):
                host = re.search('(^[^\|]+)\|.*' + folder, hostandtag).group(1)
            # check if host is monitored by check_mk
            if re.search('\|offline.*' + folder, hostandtag):
                isoffline = 'Yes'
            else:
                LOGGER.error("please make sure cmk don't monitor this host " \
                             + host)
            ipaddr = host

            # get device type from host when no found devicetype in snmp rule
            for key in host_attributes:
                if key == host:
                    if  'huaweiDeviceType' in host_attributes[key]:
                        devicetypeforhost = \
                        host_attributes[key]['huaweiDeviceType']
                    if 'ipaddress' in host_attributes[key]:
                        ipaddr = \
                        host_attributes[key]['ipaddress']

            devicetype = ''
            if devicetypeforrule == 'None':
                devicetype = devicetypeforhost
            else:
                devicetype = devicetypeforrule
            if devicetype == '':
                LOGGER.error("no found devicetype for host " \
                              + host + " stop to configure")

            isip = 'No'
            if re.search('^\d+\.\d+\.\d+\.\d+$', ipaddr):
                isip = 'Yes'
            else:
                LOGGER.error("no found the ipaddress of " \
                             + host + "stop to configure")

            # make sure hostname and ipaddress is not duplicate
            if host not in GLOABLE_HOSTS \
            and ipaddr and ipaddr not in GLOABLE_IPS \
            and isip == 'Yes' and isoffline == 'Yes' and devicetype:
                GLOABLE_HOSTS.append(host)
                GLOABLE_IPS.append(ipaddr)
                hostdic = []
                hostdic.append(host)
                hostdic.append(devicetype)
                hostdic.append(ipaddr)
                hostlist.append(hostdic)
            elif ipaddr in GLOABLE_IPS:
                LOGGER.error('duplicate ipaddress:' + ipaddr)
    return hostlist

def getHostsFromRule(monitoredhosts, devicetypeforrule, snmpdic):
    '''
    ' Methods : getHostsFromRule
    ' input: monitoredhosts, devicetypeforrule,snmpdic
    ' return hostslist with devicetype
    '''
    hostlist = []
    if devicetypeforrule != 'None':
        for host in monitoredhosts.replace('\n',',').split(','):
            hostdic = []
            #range ips,e.g. 192.168.10.*,192.168.8.20-50
            if re.search('^\d+\.\d+\.\d+\.(\d+)-(\d+)$', host) \
            or re.search('^\d+\.\d+\.\d+\.\*$', host):
                ip_before = ''
                ip_start = ''
                ip_end = ''
                if '-' in host:
                    ip_before = \
                    re.search('(\d+\.\d+\.\d+\.\d+)-\d+', host).group(1)
                    ip_start = \
                    re.search('\d+\.\d+\.\d+\.(\d+)-\d+', host).group(1)
                    ip_end = \
                    re.search('\d+\.\d+\.\d+\.\d+-(\d+)', host).group(1)
                if '*' in host:
                    ip_before = \
                    re.search('(^\d+\.\d+\.\d+\.)\*', host).group(1) + '1'
                    ip_start = '1'
                    ip_end = '254'
                if ip_start and ip_end \
                and 1 <= int(ip_start) < int(ip_end) < 255:
                    count =  int(ip_end) - int(ip_start) + 1
                    range_ips = getIp(ip_before, count)
                    for ipaddr in range_ips:
                        hostrangedic = []
                        if ipaddr not in GLOABLE_HOSTS \
                        and ipaddr not in GLOABLE_IPS:
                            # add host when snmp test successful
                            if len(snmpdic) ==3 or len(snmpdic) ==5:
                                issnmpok = snmpTest(snmpdic, ipaddr)
                                if issnmpok == 'Yes':
                                    GLOABLE_HOSTS.append(ipaddr)
                                    GLOABLE_IPS.append(ipaddr)
                                    hostrangedic.append(ipaddr)
                                    hostrangedic.append(devicetypeforrule)
                                    hostlist.append(hostrangedic)
                        else:
                            LOGGER.error('duplicate ipaddress:' + ipaddr)
                else:
                    LOGGER.error("wrong input:" + host)
            elif re.search('^\d+\.\d+\.\d+\.\d+$', host):
                # host input like 192.168.11,192.168.8.12
                ipaddr = host
                # make sure hostname and ipaddress is not duplicate
                if host not in GLOABLE_HOSTS \
                and ipaddr and ipaddr not in GLOABLE_IPS:
                    GLOABLE_HOSTS.append(host)
                    GLOABLE_IPS.append(ipaddr)
                    hostdic.append(host)
                    hostdic.append(devicetypeforrule)
                    hostlist.append(hostdic)
                else:
                    LOGGER.error('duplicate ipaddress:' + ipaddr)
            else:
                if host:
                    LOGGER.error("just support ip/range input,wrong input:" \
                    + host)
    else:
        LOGGER.error("no found devicetype for hosts monitoredhosts:" \
                     + monitoredhosts + 'stop to configure')
    return hostlist

def getHostAttribute(snmp_community):
    '''
    ' Methods : getHostAttribute
    ' return hostattributes
    '''
    hostattributes = []
    folder = ''
    snmpversion = ''
    community = ''
    snmpdic = []
    trapdic = []

    devicetypeforrule = ''
    monitoredhosts = ''
    description = ''

    # get folder position
    if len(snmp_community) == 4:
        # get folder position
        folderpos = snmp_community[len(snmp_community)-3]
        # get folder from snmp rule selection
        if len(folderpos) > 0:
            folderpath = folderpos[len(folderpos)-1]
            if re.search('\/wato\/(.+)\/\+', folderpath):
                folder = re.search('\/wato\/(.+)\/\+', folderpath).group(1)
        if folder == '':
            folder = 'Main directory'
        # get devicetype
        if 'huaweiDeviceType' in snmp_community[len(snmp_community)-1]:
            devicetypeforrule = \
            snmp_community[len(snmp_community)-1]['huaweiDeviceType']
        # get monitored hosts from rule options
        if 'monitoredHosts' in snmp_community[len(snmp_community)-1]:
            monitoredhosts = \
            snmp_community[len(snmp_community)-1]['monitoredHosts']
        # get the description info
        if 'description' in snmp_community[len(snmp_community)-1]:
            description = \
            snmp_community[len(snmp_community)-1]['description']
        # get collection snmp info
        if 'hwCollCredential' in snmp_community[len(snmp_community)-1]:
            snmpport, snmpversion, community = '', '', ''
            hwcollcredential = \
            snmp_community[len(snmp_community)-1]['hwCollCredential']
            if len(hwcollcredential) == 3:
                # snmp version v1/2c
                if re.search('^\d+$', hwcollcredential[2]):
                    snmpport = hwcollcredential[2]
                else:
                    snmpport = '161'
                    LOGGER.info("wrong snmpport input " + hwcollcredential[2])
                if 'collSNMPv1' in hwcollcredential:
                    snmpversion = 'v1'
                    community = hwcollcredential[1]
                if 'collSNMPv2' in hwcollcredential:
                    snmpversion = 'v2'
                    community = hwcollcredential[1]
                #snmp v1/2c
                if snmpversion and community and snmpport:
                    snmpdic.append(encrypt(community, folder))
                    snmpdic .append(snmpversion)
                    snmpdic .append(snmpport)
            elif len(hwcollcredential) == 6:
                snmpversion = 'v3'
                user = hwcollcredential[2]
                pwd = hwcollcredential[3]
                authprotocol = hwcollcredential[1].upper()
                privprotocol = hwcollcredential[4].upper()
                if re.search('^\d+$', hwcollcredential[5]):
                    snmpport = hwcollcredential[5]
                else:
                    snmpport = '161'
                    LOGGER.error("wrong snmpport input " + hwcollcredential[5])
                if user and pwd and snmpport:
                    snmpdic.append(user)
                    snmpdic.append(encrypt(pwd, folder))
                    snmpdic.append(authprotocol)
                    snmpdic.append(privprotocol)
                    snmpdic .append(snmpport)
            
        # get trap snmp info
        if 'hwTrapCredential' in snmp_community[len(snmp_community)-1]:
            hwtrapcredential = \
            snmp_community[len(snmp_community)-1]['hwTrapCredential']
            trapsnmpversion, trapcommunity = '', ''
            if len(hwtrapcredential) == 2:
                # trap snmp version v1/2c
                if 'trapSNMPv1' in hwtrapcredential:
                    trapsnmpversion = 'v1'
                    trapcommunity = hwtrapcredential[1]
                if 'trapSNMPv2' in hwtrapcredential:
                    trapsnmpversion = 'v2'
                    trapcommunity = hwtrapcredential[1]
                #trap snmp v1/2c
                if trapsnmpversion and trapcommunity:
                    trapdic.append(encrypt(trapcommunity, folder))
                    trapdic .append(trapsnmpversion)
                    trapdic.append('161')
            elif len(hwtrapcredential) == 5:
                trapuser = hwtrapcredential[2]
                trappwd = hwtrapcredential[3]
                trapauthprotocol = hwtrapcredential[1].upper()
                trapprivprotocol = hwtrapcredential[4].upper()
                if trapuser and trappwd:
                    trapdic.append(trapuser)
                    trapdic.append(encrypt(trappwd, folder))
                    trapdic.append(trapauthprotocol)
                    trapdic.append(trapprivprotocol)
                    trapdic.append('161')
    hostlist = []
    if len(snmpdic) > 0 and len(trapdic) == 0:
        trapdic = snmpdic
        LOGGER.info("no vaild trap acount for description " \
                        + description + " in " + folder \
                        + " so set trapAcount = collectacount")
    elif len(trapdic) > 0 and len(snmpdic) == 0:
        snmpdic =  trapdic
        LOGGER.info("no vaild collect acount for description " \
                        + description + " in " + folder \
                        + " so set collectAcount = trapAcount, port = 161")
    elif len(trapdic) == 0 and len(snmpdic) == 0:
        LOGGER.info("no vaild collect and trap acount for description " \
                        + description + " in " + folder)
    if len(snmpdic) > 0:
        regexforhost = \
        '\d+\.\d+\.\d+\.\d+-\d+|\d+\.\d+\.\d+\.\*|\d+\.\d+\.\d+\.\d+'
        if re.search(regexforhost, monitoredhosts):
            # select hosts in monitoredhosts list in rule options
            hostlist = \
            getHostsFromRule(monitoredhosts, devicetypeforrule, snmpdic)
        else:
            # select hosts in folder
            hostlist = getHostsFromFolder(folder, devicetypeforrule)
    if len(hostlist) == 0:
        LOGGER.info("no vaild hosts for description " \
                        + description + " in " + folder)
    if len(hostlist) > 0 and folder and len(snmpdic) > 0 and len(trapdic) > 0:
        hostattributes.append(hostlist)
        hostattributes.append(folder)
        hostattributes.append(snmpdic)
        hostattributes.append(trapdic)
    return hostattributes

def getHostServicesContent(devicetype, hostname, hostalias, ipaddress):
    '''
    ' get services content by reading
    ' MODULES_DIR/huawei_server/HDorRack.cfg
    ' MODULES_DIR/huawei_server/Blade.cfg
    ' Blade services: alarm
    ' Rack or HighDensity:alarm,system,fan,cpu,memory,power,hardDisk
    '''
    # create a blade tmp file for services configuration for current host
    if devicetype == 'Blade':
        commands.getoutput("cat " + MODULES_DIR \
                 + "/huawei_server/Blade.cfg > /tmp/huaweitmp.cfg")
    # create a rack or HD tmp file for services configuration for current host
    if devicetype != 'Blade' and devicetype != '':
        commands.getoutput("cat " + MODULES_DIR \
                 + "/huawei_server/HDorRack.cfg > /tmp/huaweitmp.cfg")
    # update hostname in tmp file
    if hostname:
        commands.getoutput("sed -i 's/hostname/" + hostname \
                 + "/g' /tmp/huaweitmp.cfg")
    # update hostalias in tmp file
    if hostalias:
        commands.getoutput("sed -i 's/hostalias/" + hostalias \
                 + "/g' /tmp/huaweitmp.cfg")
    # update ipaddress in tmp file
    if ipaddress:
        commands.getoutput("sed -i 's/ipaddress/" + ipaddress \
                 + "/g' /tmp/huaweitmp.cfg")
    # get tmp file content about services for host
    output = commands.getoutput("cat /tmp/huaweitmp.cfg")
    commands.getoutput("rm -rf /tmp/huaweitmp.cfg")
    return output

def getListenerContent():
    '''
    ' get listener content by reading
    ' MODULES_DIR/huawei_server/listener.cfg
    '''
    output = commands.getoutput("cat " + MODULES_DIR \
            + "/huawei_server/listener.cfg")
    return output

def startToConfig():
    '''
    ' Methods startToConfig:
    ' configure hosts,snmp credentials to file
    ' /usr/local/nagios/etc/huawei_server/huawei_hosts.xml
    ' /usr/local/nagios/etc/huawei_server/hw_server.xml
    '''
    # check environments
    checkEnv()
    impl = minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'hosts' , None)
    commands.getoutput("sudo rm -rf " \
            + NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg")
    servicefile = open(NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg",'w')
    LOGGER.info("start to config ........")

    for snmp_community in snmp_communities:
        # check if huawei's configuration
        ishuaweiconfig = ''
        description = ''
        if len(snmp_community) == 4:
            for key in snmp_community[len(snmp_community)-1]:
                if key == 'description':
                    description = snmp_community[len(snmp_community)-1][key]
                if key == 'isHuaweiCfg':
                    ishuaweiconfig = snmp_community[len(snmp_community)-1][key]

        if ishuaweiconfig != 'Yes':
            LOGGER.info("ishuaweiconfig = " + ishuaweiconfig \
                + ",not huawei plugin configuration for description "\
                + description)
            continue

        # host attribute:hostlist,snmp info,trap info
        snmpport, collectuser, encryptpwd, snmpversion, cmtyencryptpwd, \
        authprotocol, authprotocol =  '', '', '', '', '', '', ''
        trapuser, trapencryptpwd, trapsnmpversion, trapcmtyencryptpwd, \
        trapauthprotocol, trapprivprotocol = '', '', '', '', '', ''

        LOGGER.info("###############################################")
        hostattributes = getHostAttribute(snmp_community)
        if len(hostattributes) != 4:
            LOGGER.error("invaild Huawei config for description " \
                        + description)
            continue
        folder = hostattributes[1]
        if description == '':
            description = 'No set'
        LOGGER.info("rule description:" + description + ",folder:" + folder)
        allhosts = hostattributes[0]
        LOGGER.info(allhosts)
        snmpdic = hostattributes[2]
        trapdic = hostattributes[3]
        LOGGER.info("collect/trap acount:")

        if len(snmpdic) == 3:
            cmtyencryptpwd = snmpdic[0]
            encryptpwd = cmtyencryptpwd
            snmpversion = snmpdic[1]
            snmpport = snmpdic[2]
            LOGGER.info("snmpversion:" + snmpversion + ",community:******" \
                        + "snmpport:" + snmpport)
        elif len(snmpdic) == 5:
            snmpversion = 'v3'
            collectuser = snmpdic[0]
            encryptpwd = snmpdic[1]
            authprotocol = snmpdic[2]
            privprotocol = snmpdic[3]
            snmpport = snmpdic[4]
            cmtyencryptpwd = encryptpwd
            LOGGER.info("user:" + collectuser + ",password:******" \
                        + ",authprotocol:" + authprotocol \
                        + ",privprotocol:" + privprotocol \
                        + ",snmpport:" + snmpport)
       
        if len(trapdic) == 3:
            trapcmtyencryptpwd = trapdic[0]
            trapencryptpwd = trapcmtyencryptpwd
            trapsnmpversion = trapdic[1]
            LOGGER.info("trapsnmpversion:" + trapsnmpversion \
                         + ",trapcommunity:******")
        elif len(trapdic) == 5:
            trapsnmpversion = 'v3'
            trapuser = trapdic[0]
            trapencryptpwd = trapdic[1]
            trapcmtyencryptpwd = trapencryptpwd
            trapauthprotocol = trapdic[2]
            trapprivprotocol = trapdic[3]
            LOGGER.info("trapuser:" + trapuser + ",password:******" \
                             + ",trapauthprotocol:" + trapauthprotocol\
                             + ",trapprivprotocol:" + trapprivprotocol)
        if snmpversion != 'v3':
            collectuser = 'HUAWEIDEVICE'
            authprotocol = 'SHA'
            privprotocol = 'AES'
        if trapsnmpversion != 'v3':
            trapuser = 'HUAWEIDEVICE'
            trapauthprotocol = 'SHA'
            trapprivprotocol = 'AES'
        if snmpport == '':
            snmpport = '161'
            

        LOGGER.info("###############################################")

        for host in hostattributes[0]:
            host1 = host[0]
            hostname = host1
            ipaddress = host1
            devtype = host[1]
            ipaddress = hostname
            if len(host) == 3:
                ipaddress = host[2]
            # configure services info for Rack,Blade and HD to hw_server.cfg
            hostalias = hostname
            if devtype == 'Rack':
                hostalias = 'RackDetailsStatus@' + hostname
            elif devtype == 'HighDensity':
                hostalias = 'HighDensityDetailsStatus@' + hostname
            elif devtype == 'Blade':
                hostalias = 'BladeDetailsStatus@' + hostname
            cfgcontent = \
            getHostServicesContent(devtype, hostname, hostalias, ipaddress)
            servicefile.writelines(cfgcontent)

            # config snmp credentials and trap credentials to huawei_host.xml
            # hostname/ipaddress/devicetype/port
            root = dom.documentElement
            xhost = dom.createElement( 'host' )
            root.appendChild(xhost)
            xdevice = dom.createElement( 'device' )
            xhost.appendChild(xdevice)
            xhostname = dom.createElement( 'hostname' )
            xhostnamet = dom.createTextNode(hostname)
            xhostname.appendChild(xhostnamet)
            xdevice.appendChild(xhostname)
            xipaddress = dom.createElement( 'ipaddress' )
            xipaddresst = dom.createTextNode(ipaddress)
            xipaddress.appendChild(xipaddresst)
            xdevice.appendChild(xipaddress)
            xdevicetype = dom.createElement( 'devicetype' )
            xdevicetypet = dom.createTextNode(devtype)
            xdevicetype.appendChild(xdevicetypet)
            xdevice.appendChild(xdevicetype)
            xport = dom.createElement( 'port' )
            xportt = dom.createTextNode(snmpport)
            xport.appendChild(xportt)
            xdevice.appendChild(xport)
            # collect info: collectuser/password/authprotocol/privprotocol
            xcollect = dom.createElement( 'collect' )
            xhost.appendChild(xcollect)
            xsnmpversion = dom.createElement( 'snmpversion' )
            xsnmpversiont = dom.createTextNode(snmpversion)
            xsnmpversion.appendChild(xsnmpversiont)
            xcollect.appendChild(xsnmpversion)
            xuser = dom.createElement( 'user' )
            xusert = dom.createTextNode(collectuser)
            xuser.appendChild(xusert)
            xcollect.appendChild(xuser)
            xpass = dom.createElement( 'pass' )
            xpasst = dom.createTextNode(encryptpwd)
            xpass.appendChild(xpasst)
            xcollect.appendChild(xpass)
            xauthprotocol = dom.createElement( 'authprotocol' )
            xauthprotocolt = dom.createTextNode(authprotocol)
            xauthprotocol.appendChild(xauthprotocolt)
            xcollect.appendChild(xauthprotocol)
            xprivprotocol = dom.createElement( 'privprotocol' )
            xprivprotocolt = dom.createTextNode(privprotocol)
            xprivprotocol.appendChild(xprivprotocolt)
            xcollect.appendChild(xprivprotocol)
            xcommunity = dom.createElement( 'community' )
            xcommunityt = dom.createTextNode(cmtyencryptpwd)
            xcommunity.appendChild(xcommunityt)
            xcollect.appendChild(xcommunity)
            # alarm info: trapuser/trapwd/trapauthprotocol/trapprivprotocol
            xalarm = dom.createElement( 'alarm' )
            xhost.appendChild(xalarm)
            xtrapsnmpversion = dom.createElement( 'snmpversion' )
            xtrapsnmpversiont = dom.createTextNode(trapsnmpversion)
            xtrapsnmpversion.appendChild(xtrapsnmpversiont)
            xalarm.appendChild(xtrapsnmpversion)
            xtrapuser = dom.createElement( 'user' )
            xtrapusert = dom.createTextNode(trapuser)
            xtrapuser.appendChild(xtrapusert)
            xalarm.appendChild(xtrapuser)
            xtrappass = dom.createElement( 'pass' )
            xtrappasst = dom.createTextNode(trapencryptpwd)
            xtrappass.appendChild(xtrappasst)
            xalarm.appendChild(xtrappass)
            xtrapauthprotocol = dom.createElement( 'authprotocol' )
            xtrapauthprotocolt = dom.createTextNode(trapauthprotocol)
            xtrapauthprotocol.appendChild(xtrapauthprotocolt)
            xalarm.appendChild(xtrapauthprotocol)
            xtrapprivprotocol = dom.createElement( 'privprotocol' )
            xtrapprivprotocolt = dom.createTextNode(trapprivprotocol)
            xtrapprivprotocol.appendChild(xtrapprivprotocolt)
            xalarm.appendChild(xtrapprivprotocol)
            xtrapcommunity = dom.createElement( 'community' )
            xtrapcommunityt = dom.createTextNode(trapcmtyencryptpwd)
            xtrapcommunity.appendChild(xtrapcommunityt)
            xalarm.appendChild(xtrapcommunity)

            LOGGER.info(ipaddress + ' Configuration Successful;')
    commands.getoutput("sudo rm -rf " \
             + NAGIOS_DIR + "/etc/huawei_server/huawei_hosts.xml")
    xmlfile = open(NAGIOS_DIR + '/etc/huawei_server/huawei_hosts.xml' , 'w')
    dom.writexml(xmlfile, addindent = '    ' , newl = '\n' , encoding = 'UTF-8')
    xmlfile.close()

    #configure for Nagios plugin listener to hw_server.cfg
    servicefile.writelines(getListenerContent())
    servicefile.close()

    if len(GLOABLE_IPS) < 1:
        commands.getoutput("sudo rm -rf " \
                + NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg")
        commands.getoutput("sudo rm -rf " \
                + NAGIOS_DIR + "/etc/huawei_server/huawei_hosts.xml")
        commands.getoutput("sudo cp " \
                + MODULES_DIR + "/huawei_server/huawei_hosts.xml " \
                + NAGIOS_DIR + "/etc/huawei_server/")
        commands.getoutput("sudo cp " \
                + MODULES_DIR + "/huawei_server/hw_server.cfg " \
                + NAGIOS_DIR + "/etc/huawei_server/")
        LOGGER.error("no found vaild hosts! ")

    commands.getoutput("sudo chown nagios.nagios " \
            + NAGIOS_DIR + "/etc/huawei_server/huawei_hosts.xml")
    commands.getoutput("sudo chown nagios.nagios " \
            + NAGIOS_DIR + "/etc/huawei_server/hw_server.cfg")
    commands.getoutput("sudo chown nagios.nagios " \
            + MODULES_DIR + "/logsforhuawei/*")
    commands.getoutput("sudo chmod 664 " \
            + MODULES_DIR + "/logsforhuawei/*")
    commands.getoutput("sudo chown nagios.nagios " \
            + MODULES_DIR + "/logsforhuawei")
    commands.getoutput("sudo chmod 775 " \
            + MODULES_DIR + "/logsforhuawei")
    LOGGER.info("completed!")
startToConfig()
