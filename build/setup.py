#coding=utf-8
'''
Created on 2018-4-2

'''

from optparse import OptionParser
import sys
import os 
import commands
import time

NAGIOS_PLUGIN  = 'Huawei\ eSight\ Server\ Management\ Plug-in\ \(for\ Nagios\).gz'
NAGIOS_PLUGIN_NAME="Huawei\ eSight\ Server\ Management\ Plug-in\ \(for\ Nagios\)"
NAGIOS_PLUGIN_NAME2="Huawei eSight Server Management Plug-in (for Nagios)"
CURREN_PATH   = os.path.abspath('.')
SITESUSER='prod'

def checkckmVersion () :
    tempcmd ="cmk --version |grep 'check_mk version'"
    output =  commands.getoutput(tempcmd)
    if '1.2' in  output:
        return '1_2'  
    return "1_4"

def VerifyPythonVersion():
    if str(sys.version_info[0]) == '2' and str(sys.version_info[1]) =='7' and str(sys.version_info[2])=='13':
        PythonPath=sys.executable
        print PythonPath[:-6]
        return PythonPath[:-6]
    else :
        print "check python vesion fail ,please check you python is 2.7.13" 
        sys.exit(1)           
   
def uninstall(nagios_dir):
    if not os.path.isdir(CURREN_PATH+os.path.sep+NAGIOS_PLUGIN_NAME2):
        temcmd="tar zxvf %s > /dev/null 2>&1"%NAGIOS_PLUGIN
        os.system(temcmd)   

    if checkckmVersion () =="1_4":
     # create a sites user file 
        usrfilepath =CURREN_PATH+"/"+NAGIOS_PLUGIN_NAME+"/usrFile.cfg" 
        creatUserfile (usrfilepath,SITESUSER)
    tmpcmd ="chmod +x *.sh"
    os.system(tmpcmd)
    temcmd ="./uninstall.sh "
    print "temcmd",temcmd 
    os.system(temcmd)
    if os.path.isdir(CURREN_PATH+os.path.sep+NAGIOS_PLUGIN_NAME2) :
        temcmd ="cd %s/%s ;python setup.py uninstall -n %s -m %s "%(CURREN_PATH,NAGIOS_PLUGIN_NAME,nagios_dir, checkckmVersion() ) 
        print "temcmd",temcmd 
        os.system(temcmd)
def creatUserfile(filepath,cmkuser):
    path2 = filepath.replace("\\",'')
    if  not os.path.isfile(path2):
        tmpcmd =" touch "+filepath
        os.system(tmpcmd)
    file=None 
    strUsertmp ="usr="
    strGrouptmp="group="
    strUser="usr=%s\n"%cmkuser
    strGroup="group=%s\n"%cmkuser  
    
    try:
        file = open(path2,"r+")
        strlist=file.readlines()
        file.close() 
        if len(strlist) <= 1 :
            strlist.append(strUser)
            strlist.append(strGroup)
        else:
            for i in range (len(strlist)):
                if strUsertmp in str (strlist[i]):
                    strlist[i] = strUser
                if strGrouptmp in str (strlist[i]):
                    strlist[i] = strGroup         
        file=open(path2,"w")       
        file.writelines(strlist)  
    except Exception ,err:
        print "create user file error : " + str(err)
    finally:
        if file is not None :
            file.close()        
def editCmkSites (sitesUser):
    if not os.path.isdir( "/omd/sites/%s"%sitesUser):
        print "error: the site : %s not exit ,please create first !"%sitesUser
        exit()
        #tmpcmd ="omd create %s"%sitesUser
        #os.system(tmpcmd)
    #tmpdir="/tmp/%s"%(time.time())
    #if not os.path.isdir(tmpdir):
    #    tmpcmd = "mkdir %s"%(tmpdir)
    #    os.system(tmpcmd)
    # create a own module files for sitesUser      
    #tmpcmd="cp -r /omd/sites/%s/share/*  %s"%(sitesUser, tmpdir)
    #os.system(tmpcmd)
    
    #tmpcmd ="rm -rf /omd/sites/%s/share "%sitesUser
    #os.system(tmpcmd)
    
    #tmpcmd ="mkdir /omd/sites/%s/share"%sitesUser
    #os.system(tmpcmd)

    #tmpcmd ="cp -r %s/* /omd/sites/%s/share"%(tmpdir,sitesUser)
    #os.system(tmpcmd)

    tmpcmd ="chmod -R 777  /omd/sites/%s/share/check_mk/modules"% (sitesUser)
    os.system(tmpcmd)
    
    #tmpcmd ="rm  -r %s"% tmpdir
    #os.system(tmpcmd)

    

def install( localAddress ,nagiosDir, listenPort  ):
    #install nagios plugin
    if  nagiosDir is None :  
        print  "error nagios dir is none  please check you cmd "
        return 
    if  localAddress is None :  
        print  "error local address  is none  please check you cmd "
        return 
    if  listenPort is None :  
        print  "error listen port  is none  please check you cmd "
        return 
    temcmd="tar zxvf %s > /dev/null 2>&1"%NAGIOS_PLUGIN
    os.system(temcmd) 
    tmpcmd ="chmod +x *.sh"
    os.system(tmpcmd)
    checkmkVersion= checkckmVersion () 
    pythonPath= VerifyPythonVersion()
    if  checkmkVersion == "1_2":
        
        temcmd="cd %s/%s ; %s/python setup.py install -d %s -n %s -p %s "% \
            (CURREN_PATH,NAGIOS_PLUGIN_NAME,pythonPath,localAddress,nagiosDir,listenPort) 
        print "temcmd",temcmd 
        
        os.system(temcmd) 
    
    elif  checkmkVersion == "1_4" :
        # create a sites user file 
        usrfilepath =CURREN_PATH+"/"+NAGIOS_PLUGIN_NAME+"/usrFile.cfg" 
        creatUserfile (usrfilepath,SITESUSER) 
        #  
        editCmkSites(SITESUSER)
        # install nagios plugin 
        temcmd="cd %s/%s ; %s/python setup.py install -d %s -n %s -p %s -m 1_4"% \
            (CURREN_PATH,NAGIOS_PLUGIN_NAME,pythonPath,localAddress,nagiosDir,listenPort) 
        print "temcmd" ,temcmd
        os.system(temcmd) 
    else:
        temcmd="cd %s/%s ; %s/python setup.py install -d %s -n %s -p %s -m 1_4"% \
            (CURREN_PATH,NAGIOS_PLUGIN_NAME,pythonPath,localAddress,nagiosDir,listenPort) 
        print "temcmd",temcmd 
        os.system(temcmd)
        pass 
    #install checkmk plugin 
    temcmd ="./setup.sh "
    print "temcmd" ,temcmd
    os.system(temcmd)


def main():
    global SITESUSER
    MSG_USAGE = '''\n    %prog install -d LOCAL_ADDRESS [-p LISTEN_PORT] -n NAGIOS_DIR \
                   \nor\
                   \n    %prog uninstall -n NAGIOS_DIR  
                '''
    optParser = OptionParser(MSG_USAGE)
    optParser.add_option("-d", "--local_address", action="store"
                         , dest="local_address"
                         , help="Local IP address (mandatory).  "
                         + "example:192.168.1.1")
    
    optParser.add_option("-p", "--listen_port", action="store"
                         , dest="listen_port" , default='10061'
                         , help="Listening port number. Default value: 10061")
    
    optParser.add_option("-n", "--nagios_dir", action="store"
                         , dest="nagios_dir"
                         , help="Nagios home directory (mandatory).         "
                         + "Example:/usr/local/nagios")
    optParser.add_option("-u", "--cmk_user", action="store"
                         , dest="cmk_user"
                         , help="checkmk sites user only for check version 1.4 or later "
                         + "default: ")  
                                       
    options, args = optParser.parse_args()
    if checkckmVersion() ==  '1_4':
        if  options.cmk_user  is None  :
            print "please import the sites which you want to install or uninstall  checkmk plugin "  
            exit() 
    if options.nagios_dir is None:
        print "please import  the dir which you want to install or uninstall nagios plugin"
        exit() 
    if len(args) <1:
        optParser.print_help()
        exit (1)
    if len(args) == 1 and (args[0] == 'install' or  args[0] == 'uninstall'):
        SITESUSER = options.cmk_user
        if args[0] == 'uninstall':
            uninstall(options.nagios_dir) 
        elif args[0] == 'install': 
            install(options.local_address, options.nagios_dir, options.listen_port)    
        else :
            optParser.print_help()
    else:
        optParser.print_help()
main()        