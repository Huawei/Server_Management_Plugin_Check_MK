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
_health_str = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "ABSENCE", 4: "UNKOWN"}

def inventory_hw_memory_health(info):
    return [('MEMORY status', None)]

def check_hw_memory_health(item, params, info):
    _health_status = 3
    _msg = ''
    try:
        for state in info[0][0]:
            _health_status = _health_map.get(state)
        for state, index in info[1]:
            _each_status = _health_map.get(state)
            if _each_status is not None:
                if _each_status == 3:
                    continue
                _health_msg = _health_str.get(_each_status)
                _msg = _msg + " %s health status is %s;" % (str(index), _health_msg)
        return _health_status, "healthy status is %s, %s" % (_health_str.get(_health_status), _msg)
    
    except IndexError:
        return "healthy status is not queried."

check_info["huawei_ibmc_memory_check"] = {
    "inventory_function": inventory_hw_memory_health,
    "check_function": check_hw_memory_health,
    "service_description": "%s",
    "includes": ["huawei_ibmc_util_.include"],
    "snmp_info": [
        (".1.3.6.1.4.1.2011.2.235.1.1.16", ["1.0", ]),
        (".1.3.6.1.4.1.2011.2.235.1.1.16", ["50.1.6", "50.1.10"])
    ],
    "snmp_scan_function": scan,
}