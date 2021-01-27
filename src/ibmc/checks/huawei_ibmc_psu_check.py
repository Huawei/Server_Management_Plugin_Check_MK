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

_health_map = {"1": 0, "2": 1, "3": 1, "4": 2, "5": 3, "6": 3}
_health_str = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN"}

def inventory_hw_psu_health(info):
    return [('PSU status', None)]


def check_hw_psu_health(item, params, info):
    _health_status = 3
    _msg = ''
    try:
        for state in info[0][0]:
            _health = _health_map.get(state)
            _health_status = _health
        for state, present, index in info[1]:
            if present == "2":
                _health = _health_map.get(state)
                _health_msg = _health_str.get(_health)
                _msg = _msg + "%s health is %s;" % (str(index), _health_msg)
            elif present == "1":
                _msg = _msg + "%s in-position status is ABSENT;" % str(index)
            else:
                _msg = _msg + "%s in-position status is UNKNOWN;" % str(index)
        return _health_status, "Psu healthy status is %s, %s" % (_health_str.get(_health_status), _msg)
    
    except IndexError:
        return "Psu healthy status is not queried."

check_info["huawei_ibmc_psu_check"] = {
    "inventory_function": inventory_hw_psu_health,
    "check_function": check_hw_psu_health,
    "service_description": "%s",
    "includes": ["huawei_ibmc_util_.include"],
    "snmp_info": [
        (".1.3.6.1.4.1.2011.2.235.1.1.6", ["1.0", ]),
        (".1.3.6.1.4.1.2011.2.235.1.1.6", ["50.1.7", "50.1.9", "50.1.13"])
    ],
    "snmp_scan_function": scan,
}