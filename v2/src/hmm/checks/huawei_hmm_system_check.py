#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

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


status_map = {"0": "ok", 1: "warning", 2: "warning", 3: "warning",
              4: "critical", 5: "critical", 6: "critical", 7: "critical"}
_health_map = {"0": 0, "1": 1, "2": 1, "3": 1, "4": 2, "5": 2, "6": 2, "7": 2}
_health_str = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKOWN"}
STATUS_UNKOWN = 3


def inventory_huawei_system_health(info):
    return [("system status", None)]


def check_huawei_system_health(item, params, info):
    _health_status = STATUS_UNKOWN
    if info is None or info == []:
        return _health_status, "health status is unkown;"
    _health_status = _health_map.get(info[0][0])

    if _health_status is None:
        return STATUS_UNKOWN, "health status is unkown;"
    if len(info[0]) >= 1:
        _location = info[0][1]
    else:
        _location = ''
    return _health_status, "health status is %s; unhealth locations is :%s" % (_health_str.get(_health_status), _location)


check_info["huawei_hmm_system_check"] = {
    "inventory_function": inventory_huawei_system_health,
    "check_function": check_huawei_system_health,
    "service_description": "%s",
    "snmp_info": (
        ".1.3.6.1.4.1.2011.2.82.1.82.1", [
            "1.0", "2.0"]),
}
