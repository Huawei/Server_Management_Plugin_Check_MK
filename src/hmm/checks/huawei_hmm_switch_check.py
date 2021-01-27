
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


status_map = {1: "ok", 2: "minor", 3: "major", 4: "critical"}
_health_map = {"1": 0, "2": 1, "3": 1, "4": 2}
_health_str = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKOWN"}
STATUS_UNKOWN = 3


def inventory_huawei_switch_health(info):
    return [("switch status", None)]


def check_huawei_switch_health(item, params, info):
    _health_status = STATUS_UNKOWN
    _msg = ""
    if info is None or info == []:
        return _health_status, "health status is unkown"
    for index, status in info:
        _each_status = _health_map.get(status)
        if _each_status is None:
            _msg = "%s switch %s health status is unkown; " % (
                _msg, str(index))
        else:
            if _health_status == STATUS_UNKOWN:
                _health_status = _each_status
            elif _each_status > _health_status:
                _health_status = _each_status
            else:
                pass
            _msg = "%s switch %s health status is %s; " % (
                _msg, str(index), _health_str.get(_each_status))
    return _health_status, "health status is %s; %s" % (_health_str.get(_health_status), _msg)


check_info["huawei_hmm_switch_check"] = {
    "inventory_function": inventory_huawei_switch_health,
    "check_function": check_huawei_switch_health,
    "service_description": "%s",
    "snmp_info": (
        ".1.3.6.1.4.1.2011.2.82.1.82.100.2.2001.1", [
            "1",
            "3"]),
}
