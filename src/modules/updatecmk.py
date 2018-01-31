'''
' Add 'Restarting Huawei plugin coll/trap service';
' Add 'Automatically configure Huawei config filse';
' Add 'Rule option for Huawei Credentials' to check_mk.
'''

# -*- encoding: utf-8; py-indent-offset: 4 -*-
from optparse import OptionParser 

def updateCmk():
    ''' Get args '''
    parser = OptionParser() 
    parser.add_option("-m", "--module", 
                      dest="moduledir", help="Update cmkfiles") 
    parser.add_option("-w", "--web", 
                      dest="webdir", help="Update webfiles") 

    (options, args) = parser.parse_args()
    if options.moduledir and options.webdir and len(args)==0:
        cmkpath = options.moduledir + "/check_mk.py"
        cmkwatopath = options.webdir + "/htdocs/wato.py"
        builtinpath = options.webdir + "/plugins/wato/builtin_attributes.py"
    else:
        parser.error("incorrect number of arguments")

    # Update cmk file: check_mk.py
    cmkfile = open( cmkpath, "r" )  
    cmkstr = cmkfile.read()
    addstr = '''        # cmkplugin to update Huawei configuration: start.
        trapCmd = "ps -efww | grep -E 'trapd.py|collect.py' | grep -v grep | awk '{print $2}' 2>&1"
        trapOutput = os.popen(trapCmd, "r")
        trapNum = trapOutput.read().strip("\\n").replace("\\n", " ")
        if trapNum:
            killCmd = "kill -9 " + trapNum + " 2>&1"
            killNum = os.popen(killCmd, "r")
        hwCfgCmd = "python " + modules_dir + "/huawei_auto_config.py 2>&1"
        sys.stdout.write("Configuring Huawei configuration...")
        if opt_verbose:
            sys.stderr.write("Running '%s'" % hwCfgCmd)
        sys.stderr.flush()
        hwCfgOutput = os.popen(hwCfgCmd, "r")
        outputRead = hwCfgOutput.read()
        exit_status4hw = hwCfgOutput.close()
        if not exit_status4hw:
            sys.stdout.write(tty_ok + "\\n")
        else:
            sys.stdout.write("ERROR:\\n")
            sys.stderr.write(outputRead)
            return False
        # cmkplugin to update Huawei configuration: end.
'''
    cmkpos = cmkstr.find('''        command = nagios_binary + " -vp "  + nag''')
    if cmkpos != -1:  
        cmkstr = cmkstr[:cmkpos] + addstr + cmkstr[cmkpos:]  
        cmkfile = open( cmkpath, "w" )  
        cmkfile.write( cmkstr )   
        cmkfile.close()  

    # Update cmk file: wato.py
    watofile = open( cmkwatopath, "r" )
    watostr = watofile.read()
    addstr = '''       # cmkplugin for Huawei rule option update: start.
        ( "isHuaweiCfg",
          DropdownChoice(
            choices = [
                ("No", "No"),
                ("Yes", "Yes"),
            ],
            default_value = "No",
            help =  _("(Required) For Huawei cmkplugin: Using this option you can choose whether to configure this credential into huawei_hosts.xml."),
            #title = _("Huawei Plugin"),
            title = _("IsHuaweiConfig"),
          )
        ),
        ( "huaweiDeviceType",
          DropdownChoice(
            choices = [
                ("None", "None"),
                ("Blade", "Blade"),
                ("Rack", "Rack"),
                ("HighDensity", "HighDensity"),
            ],
            default_value = "None",
            help =  _("(Optional) For Huawei cmkplugin: Using this option you can configure the device type which should be used in huawei_hosts.xml."),
            title = _("Huawei Device Type"),
          )
        ),
        ( "hwCollCredential",
          hwCollSNMPCredentials(
              title = _("Huawei Collect SNMP Credentials"),
              default_value = None,
              help =  _("(Required) For Huawei cmkplugin: Using this option you can configure the collection SNMP community/credential which will be used in huawei_hosts.xml."),
              allow_empty = False,
        )),
        ( "hwTrapCredential",
          hwTrapSNMPCredentials(
              title = _("Huawei Trap SNMP Credentials"),
              default_value = None,
              help =  _("(Required) For Huawei cmkplugin: Using this option you can configure the trap SNMP community/credential which will be used in huawei_hosts.xml."),
              allow_empty = False,
        )),
        ( "monitoredHosts",
          TextAreaUnicode(
              title = _("Huawei Monitored Hosts (ip list/range)"),
              help = _("(Optional) For Huawei cmkplugin: Using this option you can add moritored hosts as Example -- (for ip list): 192.168.11.12,192.168.11.13; (for ip range): 192.168.11.12-13,192.168.11.*; Each ip or ip range should be separated by ',' or new line."),
              cols = 80,
              rows = "auto",
        )),
        # cmkplugin for Huawei rule option update: end.
'''
    watopos = watostr.find('''        ( "description",
          TextUnicode(
            title = _("Description"),
            help = _("A description or title of this rule"),''')
    watopos = watopos + 1
    if watopos != -1:
        watostr = watostr[:watopos] + addstr + watostr[watopos:]
        watofile = open( cmkwatopath, "w" )
        watofile.write( watostr )
        watofile.close()

    # Update cmk file: builtin_attributes.py, adding hwSNMPClass.
    builtinfile = open( builtinpath, "a" )
    addstr = '''# cmkplugin for Huawei trap/coll credentials: start.

_hwsnmpv3_auth_elements = [
    DropdownChoice(
        choices = [
            ( "sha", _("SHA") ),
            ( "md5", _("MD5") ),
        ],
        title = _("Authentication protocol")
    ),
    TextAscii(
        title = _("Security name"),
        attrencode = True
    ),
    Password(
        title = _("Authentication password"),
        allow_empty = False,
        #minlen = 8,
    )
]

_hwcollsnmpv3_auth_elements = [
    DropdownChoice(
        choices = [
            ( "sha", _("SHA") ),
            ( "md5", _("MD5") ),
        ],
        title = _("Authentication protocol")
    ),
    TextAscii(
        title = _("Security name"),
        attrencode = True
    ),
    Password(
        title = _("Authentication password"),
        allow_empty = False,
        #minlen = 8,
    )
]

class hwCollSNMPCredentials(Alternative):
    def __init__(self, **kwargs):

        kwargs.update({
            "elements": [
                FixedValue("noAuthNoPrivNoSecu",
                    title = _("Please select snmp version for collect"),
                    totext = _("None"),
                ),
                Tuple(
                    title = _("SNMP community (SNMP Versions 1)"),
                    elements = [
                        FixedValue("collSNMPv1",
                            title = _("Security Level"),
                            totext = _("collectionSNMPv1"),
                        ),
                        Password(
                            title = _("SNMP community"),
                            allow_empty = False
                        ),
                        TextAscii(
                            title = _("SNMP port"),
                            attrencode = True,
                            allow_empty = True,
                            default_value = 161,
                        ),
                    ]
                ),
                Tuple(
                    title = _("SNMP community (SNMP Versions 2c)"),
                    elements = [
                        FixedValue("collSNMPv2",
                            title = _("Security Level"),
                            totext = _("collectionSNMPv2"),
                        ),
                        Password(
                            title = _("SNMP community"),
                            allow_empty = False
                        ),
                        TextAscii(
                            title = _("SNMP port"),
                            attrencode = True,
                            allow_empty = True,
                            default_value = 161,
                        ),
                    ]
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 without authentication and privacy (noAuthNoPriv)"),
                    elements = [
                        FixedValue("collSNMPv3NoAuthNoPriv",
                            title = _("Security Level"),
                            totext = _("No authentication, no privacy"),
                        ),
                        TextAscii(
                            title = _("Security name"),
                            attrencode  = True,
                            allow_empty = False
                        ),
                        TextAscii(
                            title = _("SNMP port"),
                            attrencode = True,
                            allow_empty = True,
                            default_value = 161,
                        ),
                    ]
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 with authentication but without privacy (authNoPriv)"),
                    elements = [
                        FixedValue("collSNMPv3AuthNoPriv",
                            title = _("Security Level"),
                            totext = _("authentication but no privacy"),
                        ),
                    ] + _hwcollsnmpv3_auth_elements
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 with authentication and privacy (authPriv)"),
                    elements = [
                        FixedValue("collSNMPv3AuthPriv",
                            title = _("Security Level"),
                            totext = _("authentication and encryption"),
                        ),
                    ] + _hwcollsnmpv3_auth_elements + [
                        DropdownChoice(
                            choices = [
                                ( "AES", _("AES") ),
                                ( "DES", _("DES") ),
                            ],
                            title = _("Privacy protocol")
                        ),
                        TextAscii(
                            title = _("SNMP port"),
                            attrencode = True,
                            allow_empty = True,
                            default_value = 161,
                        ),
                        #Password(
                        #    title = _("Privacy pass phrase"),
                        #    minlen = 8,
                        #),
                    ]
                ),
            ],
            "style": "dropdown",
        })

        Alternative.__init__(self, **kwargs)
class hwTrapSNMPCredentials(Alternative):
    def __init__(self, **kwargs):

        kwargs.update({
            "elements": [
                FixedValue("noAuthNoPrivNoSecu",
                    title = _("Please select snmp version for trap"),
                    totext = _("None"),
                ),
                Tuple(
                    title = _("SNMP community (SNMP Versions 1)"),
                    elements = [
                        FixedValue("trapSNMPv1",
                            title = _("Security Level"),
                            totext = _("trapSNMPv1"),
                        ),
                        Password(
                            title = _("SNMP community"),
                            allow_empty = False
                        ),
                    ]
                ),
                Tuple(
                    title = _("SNMP community (SNMP Versions 2c)"),
                    elements = [
                        FixedValue("trapSNMPv2",
                            title = _("Security Level"),
                            totext = _("trapSNMPv2"),
                        ),
                        Password(
                            title = _("SNMP community"),
                            allow_empty = False
                        ),
                    ]
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 without authentication and privacy (noAuthNoPriv)"),
                    elements = [
                        FixedValue("trapSNMPv3NoAuthNoPriv",
                            title = _("Security Level"),
                            totext = _("No authentication, no privacy"),
                        ),
                        TextAscii(
                            title = _("Security name"),
                            attrencode  = True,
                            allow_empty = False
                        ),
                    ]
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 with authentication but without privacy (authNoPriv)"),
                    elements = [
                        FixedValue("trapSNMPv3AuthNoPriv",
                            title = _("Security Level"),
                            totext = _("authentication but no privacy"),
                        ),
                    ] + _hwsnmpv3_auth_elements
                ),
                Tuple(
                    title = _("Credentials for SNMPv3 with authentication and privacy (authPriv)"),
                    elements = [
                        FixedValue("trapSNMPv3AuthPriv",
                            title = _("Security Level"),
                            totext = _("authentication and encryption"),
                        ),
                    ] + _hwsnmpv3_auth_elements + [
                        DropdownChoice(
                            choices = [
                                ( "AES", _("AES") ),
                                ( "DES", _("DES") ),
                            ],
                            title = _("Privacy protocol")
                        ),
                        #Password(
                        #    title = _("Privacy pass phrase"),
                        #    minlen = 8,
                        #),
                    ]
                ),
            ],
            "style": "dropdown",
        })

        Alternative.__init__(self, **kwargs)

# New class 'huaweiDeviceTypeAttribute' can create a new host attribuite 'huaweiDeviceType'.
class huaweiDeviceTypeAttribute(Attribute):
    def __init__(self, name):
        self._choices = [
            ("Blade", "Blade"),
            ("Rack", "Rack"),
            ("HighDensity", "HighDensity")
        ]

        self._choices_dict = dict(self._choices)

        Attribute.__init__(self, name, _("Device Type"),
                    _("Specify the protocol used to connect to the management board."))

    def paint(self, value, hostname):
        return "", self._choices_dict.get(value, value)

    def render_input(self, varprefix, value):
        html.select(varprefix + "huaweiDeviceType", self._choices, value)

    def from_html_vars(self, varprefix):
        return html.var(varprefix + "huaweiDeviceType")

declare_host_attribute(huaweiDeviceTypeAttribute("huaweiDeviceType"),
                       show_in_table = False,
                       show_in_folder = False,
                       topic = _("Huawei Options")
                       )

# cmkplugin for Huawei trap/coll credentials: end. 
'''

    builtinfile.write( addstr )
    builtinfile.close()

if __name__ == '__main__':
    updateCmk()
