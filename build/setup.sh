#!/bin/sh
# +----------------------------------------------------------------------------+
# |                  Check_MK plugin for Nagios Plugin                         | 
# +----------------------------------------------------------------------------+
echo "-----------------------------------------------------------------------------------------------"
echo "|This is a Check_MK plugin for Huawei Nagios Plugin,It is based on Check_MK and Nagios Plugin |"
echo "-----------------------------------------------------------------------------------------------"

#SRCDIR=${0%/*}
SRCDIR=$(cd `dirname $0`; pwd)
datetime=`date '+%Y-%m-%d %H:%M:%S'`
modulesdir="$(cmk --path | grep modules | grep 'Main components' |sed -rn "s/.*: (.+)\//\1/gp")"
logs="$modulesdir/logsforhuawei"
if [ ! -d "$logs" ]
then
    mkdir -p $logs
fi
touch $logs/install.log &&
chmod 664 $logs/install.log &&

# find cmk config path
webdir="$(cmk --path | grep "Check_MK's web pages" |sed -rn "s/.*: (.+)\//\1/gp" 2>>$logs/install.log)"
vardir="$(cmk --path | grep 'Base working directory' |sed -rn "s/.*: (.+)\//\1/gp" 2>>$logs/install.log)"
confdir="$(cmk --path | grep 'main.mk' |sed -rn "s/.*: (.+)\//\1/gp" 2>>$logs/install.log)"

# get nagios dir,user,group
nagiosdir="$(ps -ef | grep -E 'nagios.cfg|icinga.cfg' | grep -v grep | sed -rn "s/.* (\/.+)\/etc.*/\1/gp" |uniq 2>>$logs/install.log)"
nagiosfile="$nagiosdir/bin/nagios"
nagiosinfo=`ls -l $nagiosfile 2>>$logs/install.log`
nagiosuser="$(echo "$nagiosinfo" | sed -rn "s/^-\S+ [0-9]+ (\S+) .*/\1/gp" 2>>$logs/install.log)"
wwwgroup="$(echo "$nagiosinfo" | sed -rn "s/^-\S+ [0-9]+ (\S+) (\S+).*/\2/gp" 2>>$logs/install.log)"

if [ -f "$logs/install.log" ]
then
    chown $wwwgroup.$nagiosuser $logs/install.log
fi

# check if nagios is running
if [ -z "$nagiosdir" ]
then
    echo "$datetime This installation depends on nagios,please make sure if nagios is running,exit" |tee -a $logs/install.log
    exit
fi

# check if cmk plugin is re-installed
if [ -f "$modulesdir/huawei_auto_config.py" ]; then
  echo "$datetime please uninstall first,and then re-insall. exit" |tee -a $logs/install.log
  exit
fi

echo -n "Do you want to install this(y/n)? -> "
read todo

if [ "$todo" = "y" ]
then
  #echo "check if nagios plugin is installed in this machine"
  nagiosplugin="$nagiosdir/libexec/huawei_server/trapdcheck.sh"
  if [ -f "$nagiosplugin" ]
  then
      echo "$datetime Huawei Nagios Plugin----OK" |tee -a $logs/install.log
  else
      echo "$datetime Huawei Nagios Plugin is not installed in this machine,exit" |tee -a $logs/install.log
      exit
  fi

  #echo "check if Check_MK is installed in this machine"
  if [ -d "$modulesdir" ]
  then
      echo "$datetime Check_MK----OK" |tee -a $logs/install.log
  else
      echo "$datetime This plugin depends on Check_MK,please install Check_MK first,exit" |tee -a $logs/install.log
      exit
  fi

  
  echo "$datetime start to install,it will be installed under Check_MK correlative directory......" >> $logs/install.log
  
  #check huawei configure files
  conffilepath="$nagiosdir/etc/huawei_server"
  if [ ! -f "$conffilepath" ]
  then
      touch $conffilepath/hw_server.cfg |tee -a $logs/install.log
  fi

  cmkdir=$(echo $modulesdir |sed -rn "s/(.+)\/modules/\1/gp" 2>>$logs/install.log)

  #back up the following cmk original file to $cmkdir/uninstall/originfiles
  if [ ! -d "$cmkdir/uninstall/originfiles" ]; then
      mkdir -p $cmkdir/uninstall/originfiles
  fi
  if [ ! -f "$cmkdir/uninstall/originfiles/wato.py" ]; then
      cp $cmkdir/web/htdocs/wato.py $cmkdir/uninstall/originfiles |tee -a $logs/install.log
  fi
  if [ ! -f "$cmkdir/uninstall/originfiles/builtin_attributes.py" ]; then
      cp $cmkdir/web/plugins/wato/builtin_attributes.py $cmkdir/uninstall/originfiles |tee -a $logs/install.log 
  fi
  if [ ! -f "$cmkdir/uninstall/originfiles/check_mk.py" ]; then
      cp $modulesdir/check_mk.py $cmkdir/uninstall/originfiles |tee -a $logs/install.log
  fi
  if [ ! -f "$cmkdir/uninstall/originfiles/huawei_hosts.xml" ]; then
      cp $conffilepath/huawei_hosts.xml $cmkdir/uninstall/originfiles |tee -a $logs/install.log
  fi
  if [ ! -f "$cmkdir/uninstall/originfiles/hw_server.cfg" ]; then
      cp $conffilepath/hw_server.cfg $cmkdir/uninstall/originfiles |tee -a $logs/install.log
  fi

  #back up the following cmk files to $cmkdir/uninstall/updates
  mkdir -p $cmkdir/uninstall/updates 2>>$logs/install.log &&

  if [ ! -f "$cmkdir/uninstall/updates/huawei_hosts.xml" ]; then
      cp $conffilepath/huawei_hosts.xml $cmkdir/uninstall/updates |tee -a $logs/install.log
  fi
  if [ ! -f "$cmkdir/uninstall/updates/hw_server.cfg" ]; then
      cp $conffilepath/hw_server.cfg $cmkdir/uninstall/updates |tee -a $logs/install.log
  fi
  if [ ! -f "$cmkdir/uninstall/updates/check_mk.py" ]; then
      cp $modulesdir/check_mk.py $cmkdir/uninstall/updates |tee -a $logs/install.log
  fi
  
  cp $SRCDIR/uninstall.sh $cmkdir/uninstall |tee -a $logs/install.log &&
  if [ ! -f "$cmkdir/uninstall/updates/wato.py" ]; then
     cp $cmkdir/web/htdocs/wato.py $cmkdir/uninstall/updates |tee -a $logs/install.log
  fi

  if [ ! -f "$cmkdir/uninstall/updates/builtin_attributes.py" ]; then
     cp $cmkdir/web/plugins/wato/builtin_attributes.py $cmkdir/uninstall/updates |tee -a $logs/install.log
  fi

  # start to install cmk plugin....

  tar -xzf $SRCDIR/modulesplugin.tar.gz -C $modulesdir |tee -a $logs/install.log &&

  # user views content
  huawei_views="'agg_HighDensity': {'browser_reload': 0,
                     'column_headers': 'pergroup',
                     'context': {'hostalias': {'hostalias': 'HighDensityDetails',
                                               'neg_hostalias': ''}},
                     'datasource': 'services',
                     'description': u'HighDensity\n',
                     'force_checkboxes': False,
                     'group_painters': [('host', 'host_export', None),
                                        ('host_address', '', None)],
                     'hidden': False,
                     'hidebutton': False,
                     'icon': None,
                     'layout': 'table',
                     'linktitle': u'HighDensity',
                     'mobile': False,
                     'mustsearch': False,
                     'name': 'agg_HighDensity',
                     'num_columns': 1,
                     'owner': 'nagiosadmin',
                     'painters': [('service_state', None, None),
                                  ('service_description', None, None),
                                  ('svc_plugin_output', None, None),
                                  ('svc_state_age', None, None),
                                  ('svc_check_age', None, None)],
                     'play_sounds': False,
                     'public': False,
                     'single_infos': [],
                     'sorters': [('site', False)],
                     'title': u'Huawei High Density Server',
                     'topic': u'Huawei Nagios Plugin Views',
                     'user_sortable': True},
 'agg_alarm': {'browser_reload': 0,
               'column_headers': 'pergroup',
               'context': {'serviceregex': {'neg_service_regex': '',
                                            'service_regex': 'Alarm'}},
               'datasource': 'services',
               'description': u'Alarm\n',
               'force_checkboxes': False,
               'group_painters': [],
               'hidden': False,
               'hidebutton': False,
               'icon': None,
               'layout': 'table',
               'linktitle': u'Alarm',
               'mobile': False,
               'mustsearch': False,
               'name': 'agg_alarm',
               'num_columns': 1,
               'owner': 'nagiosadmin',
               'painters': [('service_state', None, None),
                            ('host', 'host_export', None),
                            ('host_address', None, None),
                            ('service_description', None, None),
                            ('svc_plugin_output', None, None),
                            ('svc_state_age', None, None),
                            ('svc_check_age', None, None)],
               'play_sounds': False,
               'public': False,
               'single_infos': [],
               'sorters': [('inv_software_applications_citrix_vm_desktop_group_name',
                            False)],
               'title': u'Alarm',
               'topic': u'Huawei Nagios Plugin Views',
               'user_sortable': True},
 'agg_blade': {'browser_reload': 0,
               'column_headers': 'pergroup',
               'context': {'hostalias': {'hostalias': 'BladeDetails',
                                         'neg_hostalias': ''}},
               'datasource': 'services',
               'description': u'blade\n',
               'force_checkboxes': False,
               'group_painters': [('host', 'host_export', None),
                                  ('host_address', '', None)],
               'hidden': False,
               'hidebutton': False,
               'icon': None,
               'layout': 'table',
               'linktitle': u'blade',
               'mobile': False,
               'mustsearch': False,
               'name': 'agg_blade',
               'num_columns': 1,
               'owner': 'nagiosadmin',
               'painters': [('service_state', None, None),
                            ('service_description', None, None),
                            ('svc_plugin_output', None, None),
                            ('svc_state_age', None, None),
                            ('svc_check_age', None, None)],
               'play_sounds': False,
               'public': False,
               'single_infos': [],
               'sorters': [('site_host', False)],
               'title': u'Huawei Blade Server',
               'topic': u'Huawei Nagios Plugin Views',
               'user_sortable': True},
 'agg_listener': {'browser_reload': 0,
                  'column_headers': 'pergroup',
                  'context': {'hostregex': {'host_regex': 'huawei-server-plugin',
                                            'neg_host_regex': ''}},
                  'datasource': 'services',
                  'description': u'Listener Status\n',
                  'force_checkboxes': False,
                  'group_painters': [],
                  'hidden': False,
                  'hidebutton': False,
                  'icon': None,
                  'layout': 'table',
                  'linktitle': u'Listener Status',
                  'mobile': False,
                  'mustsearch': False,
                  'name': 'agg_listener',
                  'num_columns': 1,
                  'owner': 'nagiosadmin',
                  'painters': [('service_state', None, None),
                               ('host', 'host_export', None),
                               ('service_description', None, None),
                               ('svc_plugin_output', None, None)],
                  'play_sounds': False,
                  'public': False,
                  'single_infos': [],
                  'sorters': [],
                  'title': u'Listener Status',
                  'topic': u'Huawei Nagios Plugin Views',
                  'user_sortable': True},
 'agg_problems': {'browser_reload': 0,
                  'column_headers': 'pergroup',
                  'context': {'svcstate': {'st0': '',
                                           'st1': 'on',
                                           'st2': 'on',
                                           'st3': 'on',
                                           'stp': ''}},
                  'datasource': 'services',
                  'description': u'Service Problems\n',
                  'force_checkboxes': False,
                  'group_painters': [('service_state', '', None)],
                  'hidden': False,
                  'hidebutton': False,
                  'icon': None,
                  'layout': 'table',
                  'linktitle': u'Service Problems',
                  'mobile': False,
                  'mustsearch': False,
                  'name': 'agg_problems',
                  'num_columns': 1,
                  'owner': 'nagiosadmin',
                  'painters': [('service_state', None, None),
                               ('host', 'host_export', None),
                               ('host_address', None, None),
                               ('service_description', None, None),
                               ('svc_plugin_output', None, None),
                               ('svc_state_age', None, None),
                               ('svc_check_age', None, None)],
                  'play_sounds': False,
                  'public': False,
                  'single_infos': [],
                  'sorters': [('inv_networking_wlan_controller', True),
                              ('svcstate', False)],
                  'title': u'Service Problems',
                  'topic': u'Huawei Nagios Plugin Views',
                  'user_sortable': True},
 'agg_rack': {'browser_reload': 0,
              'column_headers': 'pergroup',
              'context': {'hostalias': {'hostalias': 'Rackdetails',
                                        'neg_hostalias': ''}},
              'datasource': 'services',
              'description': u'rack\n',
              'force_checkboxes': False,
              'group_painters': [('host', 'host_export', None),
                                 ('host_address', '', None)],
              'hidden': False,
              'hidebutton': False,
              'icon': None,
              'layout': 'table',
              'linktitle': u'rack',
              'mobile': False,
              'mustsearch': False,
              'name': 'agg_rack',
              'num_columns': 1,
              'painters': [('service_state', None, None),
                           ('service_description', None, None),
                           ('svc_plugin_output', None, None),
                           ('svc_state_age', None, None),
                           ('svc_check_age', None, None)],
              'play_sounds': False,
              'public': False,
              'single_infos': [],
              'sorters': [('wato_folder_abs', False)],
              'title': u'Huawei Rack Server',
              'topic': u'Huawei Nagios Plugin Views',
              'user_sortable': True}"
   # create Huawei Nagios plugin views to user_views.mk
   if [ -f "$vardir/web/nagiosadmin/user_views.mk" ]; then
       cp $vardir/web/nagiosadmin/user_views.mk  $cmkdir/uninstall/updates |tee -a $logs/install.log
       if [ -z "$(cat $vardir/web/nagiosadmin/user_views.mk | grep 'topic' 2>>$logs/install.log)" ]
       then
            echo "{$huawei_views}" > $vardir/web/nagiosadmin/user_views.mk &&
            chown $wwwgroup.$nagiosuser $vardir/web/nagiosadmin/user_views.mk &&
            chmod 664 $vardir/web/nagiosadmin/user_views.mk
       fi

       if [ -z "$(cat $vardir/web/nagiosadmin/user_views.mk | grep 'Huawei Nagios Plugin Views')" ] && [ ! -z "$(cat $vardir/web/nagiosadmin/user_views.mk | grep 'topic')" ]
       then
            sed -i '$s/}$/,/' $vardir/web/nagiosadmin/user_views.mk 2>>$logs/install.log
            echo "$huawei_views}" >> $vardir/web/nagiosadmin/user_views.mk
       fi
  else
       mkdir -p $vardir/web/nagiosadmin &&
       echo "{$huawei_views}" > $vardir/web/nagiosadmin/user_views.mk &&
       chown $wwwgroup.$nagiosuser $vardir/web/nagiosadmin/user_views.mk |tee -a $logs/install.log&&
       chmod 664 $vardir/web/nagiosadmin/user_views.mk |tee -a $logs/install.log
  fi
  
  # setup check_mk pluin UI
  python $modulesdir/updatecmk.py -m $modulesdir -w $webdir |tee -a $logs/install.log &&
  rm -rf $modulesdir/updatecmk.py &&

  # check if cmk plugin UI setup successfully
  if [ -z "$(cat $cmkdir/web/htdocs/wato.py | grep 'hwCollCredential')" ]
  then
      echo -e "$datetime cmk plugin UI setup Failed!" |tee -a $logs/install.log
      exit
  fi
  # check if cmk plusin setup successfully.
  if [ -f "$modulesdir/huawei_auto_config.py" ]; then
      service nagios restart |tee -a $logs/install.log&&
      echo -e "$datetime Installation completed successfully.\n$datetime Please restart apache/httpd" |tee -a $logs/install.log
  else
      echo -e "$datetime installed Failed!" |tee -a $logs/install.log
      exit
  fi

else
  exit  
fi
