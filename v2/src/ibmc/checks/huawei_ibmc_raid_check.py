#!/usr/bin/python
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.


_health_map = {"0": 0, "65535": 1}
_health_str = {0: "OK", 1: "UNKNOWN", 2: "WARNING"}

def inventory_hw_raid_health(info):
    return [('RAID status', None)]

def check_hw_raid_health(item, params, info):
    _health_status = 2
    _msg = ""
    try:
        for state in info[0][0]:
            _health = _health_map.get(state)
            if _health:
                _health_status = _health

        for state, present in info[1]:
            if present == "2":
                _health = _health_map.get(state)
                if state == "0":
                    _health_msg = "OK"
                else:
                    _health_msg = "WARNING"
                _msg = "BBU health is %s." % _health_msg
            elif present == "1":
                _msg = "BBU in-position status is ABSENT."
            else:
                _msg = "BBU in-position status is UNKNOWN."
        return _health_status, "Raid healthy status is %s, %s" % (_health_str.get(_health_status), _msg)
    
    except IndexError:
        return "Raid healthy status is not queried"

check_info["huawei_ibmc_raid_check"] = {
    "inventory_function": inventory_hw_raid_health,
    "check_function": check_hw_raid_health,
    "service_description": "%s",
    "includes": ["huawei_ibmc_util_.include"],
    "snmp_info": [
        (".1.3.6.1.4.1.2011.2.235.1.1.36", ["50.1.7", ]),
        (".1.3.6.1.4.1.2011.2.235.1.1.36", ["50.1.18", "50.1.16"])
    ],
    "snmp_scan_function": scan,
}