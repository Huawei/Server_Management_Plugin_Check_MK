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


_health_map = {"1":0, "2":1, "3":1, "4":2, "5":3, "6":3}
_health_str = {0:"OK", 1:"WARNING", 2:"CRITICAL", 3:"UNKOWN"}

def inventory_hw_cpu_health(info):
    return [('CPU status', None)]
    
def check_hw_cpu_health(item, params, info):
    _health_status = 3
    _msg = ''
    try:
        for state in info[0][0]:
            _health_status = _health_map.get(state)
        for state, model, index in info[1]:
            _each_status = _health_map.get(state)
            if _each_status is None:
                _msg = _msg + "%s type %s health status is unknown" % (str(index), str(model))
            else:
                _health_msg = _health_str.get(_each_status)
                _msg = _msg + " %s type %s health status is %s;" % (str(index), str(model), _health_msg)
        return _health_status, "CPU healthy status is %s, %s" % (_health_str.get(_health_status), _msg)
    
    except IndexError:
        return "CPU healthy status is not queried."

check_info["huawei_ibmc_cpu_check"] = {
    "inventory_function": inventory_hw_cpu_health,
    "check_function": check_hw_cpu_health,
    "service_description": "%s",
    "includes": ["huawei_ibmc_util_.include"],
    "snmp_info": [
        (".1.3.6.1.4.1.2011.2.235.1.1.15", ["1.0", ]),
        (".1.3.6.1.4.1.2011.2.235.1.1.15", ["50.1.6", "50.1.4", "50.1.10"])
],
    "snmp_scan_function": scan,
}