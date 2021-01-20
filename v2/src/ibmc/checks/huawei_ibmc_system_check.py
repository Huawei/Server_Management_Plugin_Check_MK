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


_health_map = {"1":0, "2":1, "3":1, "4":2}
_health_str = {0:"OK", 1:"WARNING", 2:"CRITICAL", 3: "UNKNOWN"}

def inventory_hw_system_health(info):
    for state, model in info:
        return [(model, None)]

def check_hw_system_health(item, params, info):
    _health = 3
    _msg = ""
    for state, model in info:
        _health = _health_map.get(state)
        _health_msg = _health_str.get(_health)
        _msg = _msg + "server name is %s health is %s" % (str(model), _health_msg )
    return _health, _msg


check_info["huawei_ibmc_system_check"] = {
    "inventory_function": inventory_hw_system_health,
    "check_function": check_hw_system_health,
    "service_description": "%s",
    "includes": ["huawei_ibmc_util_.include"],
    "snmp_info": (
        ".1.3.6.1.4.1.2011.2.235.1.1.1",
        ["1.0", "6.0", ]
    ),
    "snmp_scan_function": scan,
}


