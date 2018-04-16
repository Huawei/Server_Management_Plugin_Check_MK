#!/bin/sh
#SRCDIR=${0%/*}
source /etc/profile
SRCDIR=$(cd `dirname $0`; pwd)
datetime=`date '+%Y-%m-%d %H:%M:%S'`
siteUsrFilePath=$NAGIOSHOME/etc/huawei_server/usrFile.cfg

#find cmk config path
  if [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion1_4 ] || [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion1_5 ]; then 
    siteUser=`cat $siteUsrFilePath |grep usr |awk -F = '{print $2}'`
    siteGroup=`cat $siteUsrFilePath |grep group |awk -F = '{print $2}'`
    modulesdir="/opt/omd/sites/$siteUser/share/check_mk/modules"
  else 
    modulesdir="$(cmk --path | grep modules | grep 'Main components' |sed -rn "s/.*: (.+)\//\1/gp")"
  fi
  logs="$modulesdir/logsforhuawei"
  if [ ! -d "$logs" ]
  then
      mkdir -p $logs
  fi

  touch $logs/uninstall.log &&
  chmod 664 $logs/uninstall.log &&

# find cmk dir nagios dir,user,group 
if [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion'1_4' ] || [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion'1_5' ]; then 
    vardir="/opt/omd/sites/$siteUser/var/check_mk"
    confdir="/opt/omd/sites/$siteUser/etc/check"   
    nagiosdir=$NAGIOSHOME
    nagiosfile="/omd/sites/$siteUser/bin/nagios"
    nagiosinfo=`ls -l $nagiosfile 2>>$logs/install.log`
    nagiosuser=$siteUser
    wwwgroup=$siteGroup
    webuser='cmkadmin'
    
else
  vardir="$(cmk --path | grep 'Base working directory' |sed -rn "s/.*: (.+)\//\1/gp" 2>>$logs/uninstall.log)"
  confdir="$(cmk --path | grep 'main.mk' |sed -rn "s/.*: (.+)\//\1/gp")"
  nagiosdir="$(ps -ef | grep -E 'nagios.cfg|icinga.cfg' | grep -v grep | sed -rn "s/.* (\/.+)\/etc.*/\1/gp" |uniq 2>>$logs/uninstall.log)"
  conffilepath="$nagiosdir/etc/huawei_server"
  nagiosfile="$nagiosdir/bin/nagios"
  nagiosinfo=`ls -l $nagiosfile 2>>$logs/uninstall.log`
  nagiosuser="$(echo "$nagiosinfo" | sed -rn "s/^-\S+ [0-9]+ (\S+) .*/\1/gp" 2>>$logs/uninstall.log)"
  wwwgroup=$(echo "$nagiosinfo" | sed -rn "s/^-\S+ [0-9]+ (\S+) (\S+).*/\2/gp" 2>>$logs/uninstall.log)
  webuser='nagiosadmin'
fi

  cmkdir=$(echo $modulesdir |sed -rn "s/(.+)\/modules/\1/gp" 2>>$logs/uninstall.log)
  pluginpro=$(ps -ef | grep 'huawei_auto_config.py' | grep -v 'grep' 2>>$logs/uninstall.log)

# check if nagios is running
  if [ -f "$logs/uninstall.log" ]
  then
    chown $wwwgroup.$nagiosuser $logs/uninstall.log
  fi
  if [ -z "$nagiosdir" ]
  then
    echo "$datetime This uninstallation depends on nagios,please make sure if nagios is running,exit" |tee -a $logs/install.log
    exit
  fi
# check if check_mk plugin installed
  if [ ! -f "$modulesdir/huawei_auto_config.py" ]; then
      echo "$datetime No found check_mk plugin installation on this machine. exit" |tee -a $logs/uninstall.log
      exit
  fi

# check if huawei_auto_config.py in process

  if [ ! -z "$pluginpro" ]; then
      echo "$datetime cmk plugin is running in process.Aborting" |tee -a $logs/uninstall.log
      exit
  fi
# restore check_mk original files
  rm -rf $conffilepath/huawei_hosts.xml $conffilepath/hw_server.cfg &&

  if [ -f "$cmkdir/uninstall/updates/check_mk.py" ]; then
      rm -rf $modulesdir/check_mk.py &&
      cp $cmkdir/uninstall/updates/check_mk.py $modulesdir/check_mk.py |tee -a $logs/uninstall.log
  fi
  if [ -f "$cmkdir/uninstall/updates/wato.py" ]; then
      rm -rf $cmkdir/web/htdocs/wato.py &&
      cp $cmkdir/uninstall/updates/wato.py $cmkdir/web/htdocs/wato.py |tee -a $logs/uninstall.log
  fi

  if [ -f "$cmkdir/uninstall/updates/builtin_attributes.py" ]; then
      rm -rf $cmkdir/web/plugins/wato/builtin_attributes.py &&
      cp $cmkdir/uninstall/updates/builtin_attributes.py $cmkdir/web/plugins/wato/builtin_attributes.py |tee -a $logs/uninstall.log
  fi

  rm -rf $modulesdir/cmk_base_for_huawei.py*  $modulesdir/find_nagois_dir.py*  $modulesdir/huawei_auto_config.py*  $modulesdir/huawei_server &&
  rm -rf $vardir/web/$webuser/user_views.mk &&
  rm -rf $nagiosdir/bin/huawei_server/cmkGenKey.py* &&
  
  if [ -f "$cmkdir/uninstall/updates/user_views.mk" ]; then
      cp $cmkdir/uninstall/updates/user_views.mk $vardir/web/$webuser/ |tee -a $logs/uninstall.log &&
      chown $wwwgroup.$nagiosuser $vardir/web/$webuser/user_views.mk |tee -a $logs/uninstall.log &&
      chmod 664 $vardir/web/$webuser/user_views.mk |tee -a $logs/uninstall.log
  fi

  cp $cmkdir/uninstall/originfiles/huawei_hosts.xml $conffilepath/huawei_hosts.xml |tee -a $logs/uninstall.log &&
  chown $wwwgroup.$nagiosuser $conffilepath/huawei_hosts.xml |tee -a $logs/uninstall.log &&
  cp $cmkdir/uninstall/originfiles/hw_server.cfg $conffilepath/hw_server.cfg |tee -a $logs/uninstall.log &&
  chown $wwwgroup.$nagiosuser $conffilepath/hw_server.cfg |tee -a $logs/uninstall.log &&
  rm -rf $cmkdir/uninstall/updates &&

  # check if cmk UI uninstall successfully.

  if [ ! -z "$(cat $cmkdir/web/htdocs/wato.py | grep 'hwCollCredential')" ]
  then
      echo -e "$datetime cmk plugin UI uninstall Failed!" |tee -a $logs/uninstall.log
      exit
  fi

  # check if cmk plugin uninstall successfully.
  if [ ! -f "$modulesdir/huawei_auto_config.py" ]; then
       if [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion'1_4' ] || [ cmkversion$NAGIOS_CHECKMK_VERSION == cmkversion'1_5' ]; then 
          omd restart |tee -a $logs/install.log
       else   
          service nagios restart 2>>$logs/uninstall.log 
       fi   
       echo -e "$datetime uninstall completed successfully.\n$datetime Please restart apache/httpd" | tee -a $logs/uninstall.log
  else
      echo "$datetime uninstall Failed!" | tee -a $logs/uninstall.log
      exit
  fi
